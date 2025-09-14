from ..model import SuccessResponse
from ..enums import  CollectionType
from .model import MarketplaceOnboarding, TempAccountRequest, UserStatus
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class UserHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        collection = client.db.database.get_collection(CollectionType.USERS.value)
        self.uid = client.uid
        self.db = DbManager(collection, uid=self.uid)

    async def addUserToDb(self, details: dict):
        setDict = {"name": details['name'], "email": details['email']}
        phoneNumber = details.get('phoneNumber', None)
        if phoneNumber: setDict["phone"] = phoneNumber
        await self.db.updateOne({"_id": self.uid}, setDict=setDict, upsert=True)

    async def setUserAsPaid(self):
        count, id = await self.db.updateOne({"_id": self.uid}, setDict={"status": UserStatus.PAID.value})
        return count>0

    async def getMarketplaceOnboarding(self):
        pipeline = [
            { '$lookup': { 'from': 'spapi_accounts', 'localField': '_id', 'foreignField': 'uid', 'pipeline': [ { '$project': { 'name': 1, 'countrycode': 1, 'sellerid': 1 } } ], 'as': 'spapi' } }, 
            { '$lookup': { 'from': 'advertising_accounts', 'localField': '_id', 'foreignField': 'uid', 'pipeline': [ { '$project': { 'name': 1, 'countrycode': 1, 'createdat': 1 } } ], 'as': 'ad' } }, 
            { '$lookup': { 'from': 'marketplaces', 'localField': '_id', 'foreignField': 'uid', 'pipeline': [ { '$project': { 'name': 1, 'countrycode': 1, 'storename': 1, 'marketplaceid': 1, 'status': 1} } ], 'as': 'marketplaces' } }, 
            { '$project': { 'email': 0, 'phoneNumber': 0, 'name': 0, '_id': 0 } },
            { '$set': { 'step': { '$switch': { 'branches': [ { 'case': { '$eq': [ { '$size': '$spapi' }, 0 ] }, 'then': 'Add Seller Central Account' }, { 'case': { '$eq': [ { '$size': '$ad' }, 0 ] }, 'then': 'Add Advertising Account' }, { 'case': { '$eq': [ { '$size': '$marketplaces' }, 0 ] }, 'then': 'Add Marketplace' } ], 'default': None } } } }
        ]
        data = await self.db.aggregate(pipeline)        
        if len(data)>0: return MarketplaceOnboarding.model_validate(data[0])
        raise ValueError("User not found")
    
    async def createTempAccountAdditionRequest(self, data: TempAccountRequest):
        count, id = await self.db.updateOne({"_id": self.uid}, setDict={"temp_account_request": data.model_dump(mode="json", exclude_none=True)})
        return SuccessResponse(success=count>0)

    async def getTempAccountAdditionRequest(self):
        data = await self.db.findOne({"_id": self.uid}, projectionInc=["temp_account_request"])
        return TempAccountRequest.model_validate(data["temp_account_request"])


    async def update(self, updateDict: dict):
        await self.db.updateOne({"_id": self.uid}, setDict=updateDict, upsert=True)

    async def addCredits(self, credits: int):
        await self.db.incOne({"_id": self.uid}, {"credits":  credits})

    async def deleteKeys(self, keys: list[str]):
        await self.db.deleteFields(keys, {"_id": self.uid})

    async def stopOnboarding(self):
        await self.deleteKeys(["onboarding"])

    async def getUser(self):
        return await self.db.findOne({"_id": self.uid})
    

   