from bson import ObjectId
from models.enums import CollectionType 
from models.collections.advertising_accounts import AdvertisingAccountRequest, RenameAdvertisingAccount
from db.DbUtils import DbManager
from models.model import SuccessResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

class AdvertisingAccountsHelper:
    db: DbManager
    uid: str
    db: DbManager
    
    def __init__(self, db: AsyncIOMotorDatabase, uid: str) -> None:
        self.db = DbManager(db.get_collection(CollectionType.ADVERTISING_ACCOUNTS.value), uid=uid)
        self.uid = uid

    async def addAccount(self, data: AdvertisingAccountRequest):
        await self.db.insertOne(data.model_dump(mode="json"), withUidMarketplace=True)

    async def rename(self, body: RenameAdvertisingAccount):
        count = await self.db.updateOne({"_id": ObjectId(body.id)}, setDict={"name": body.name})
        return SuccessResponse(success=count[0]>0)
    
    async def getAccountApiObject(self, id: str|ObjectId, client_id:str, client_secret:str):
        urlKey = '$ad_url'
        pipeline = [ self.db.pp.matchMarketplace({'_id': self.db.convertToObjectId(id)}), { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken"} }]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        return {**data[0], "client_id":client_id, "client_secret":client_secret, "isad": True}
