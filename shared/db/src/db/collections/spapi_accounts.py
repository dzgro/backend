from bson import ObjectId
from models.model import SuccessResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.enums import CollectionType 
from models.collections.spapi_accounts import SPAPIAccountRequest, RenameSPAPIAccount
from db.DbUtils import DbManager

class SPAPIAccountsHelper:
    db: DbManager
    uid: str
    
    def __init__(self, db: AsyncIOMotorDatabase, uid: str) -> None:
        self.db = DbManager(db.get_collection(CollectionType.SPAPI_ACCOUNTS.value), uid=uid)
        self.uid = uid

    async def getSeller(self, sellerid: str) -> dict:
        return await self.db.findOne({"sellerid": sellerid})

    async def rename(self, body: RenameSPAPIAccount):
        count = await self.db.updateOne({"_id": ObjectId(body.id)}, setDict={"name": body.name})
        return SuccessResponse(success=count[0]>0)
    
    async def addSeller(self, data: SPAPIAccountRequest):
        await self.db.insertOne(data.model_dump(mode="json"), withUidMarketplace=True)
        
    async def getAccountApiObject(self, id: str|ObjectId, client_id:str, client_secret:str):
        urlKey = '$spapi_url'
        pipeline = [ self.db.pp.matchMarketplace({'_id': self.db.convertToObjectId(id)}), { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken"} }]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        return {**data[0], "client_id":client_id, "client_secret":client_secret, "isad": False}
            
        