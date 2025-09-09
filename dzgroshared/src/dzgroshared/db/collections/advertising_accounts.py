from bson import ObjectId
from dzgroshared.models.enums import CollectionType 
from dzgroshared.models.collections.advertising_accounts import AdvertisingAccountRequest, RenameAdvertisingAccount
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.model import SuccessResponse
from dzgroshared.client import DzgroSharedClient
from dzgroshared.amazonapi.adapi import AdApiClient

class AdvertisingAccountsHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADVERTISING_ACCOUNTS.value), uid=client.uid)

    async def addAccount(self, data: AdvertisingAccountRequest):
        await self.db.insertOne(data.model_dump(mode="json"), withUidMarketplace=True)

    async def rename(self, body: RenameAdvertisingAccount):
        count = await self.db.updateOne({"_id": ObjectId(body.id)}, setDict={"name": body.name})
        return SuccessResponse(success=count[0]>0)
    
    async def getAccountApiClient(self, id: str|ObjectId, client_id:str, client_secret:str):
        urlKey = '$ad_url'
        pipeline = [ self.db.pp.matchMarketplace({'_id': self.db.convertToObjectId(id)}), { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken"} }]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        return AdApiClient(**{**data[0], "client_id":client_id, "client_secret":client_secret, "isad": True})
