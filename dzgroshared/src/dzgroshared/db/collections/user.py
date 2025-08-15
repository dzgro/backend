from bson import ObjectId
from dzgroshared.db.collections.marketplaces import MarketplaceHelper
from dzgroshared.models.model import SuccessResponse
from dzgroshared.models.enums import  CollectionType, MarketplaceStatus, BusinessType
from dzgroshared.models.collections.user import BusinessDetails
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class UserHelper:
    client: DzgroSharedClient
    db: DbManager
    marketplaceHelper: MarketplaceHelper
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str) -> None:
        self.client = client
        collection = client.db.database.get_collection(CollectionType.USERS.value)
        self.db = DbManager(collection, uid=uid)
        self.uid = uid

    async def addUserToDb(self, details: dict):
        setDict = {"name": details['name'], "email": details['email']}
        phoneNumber = details.get('phoneNumber', None)
        if phoneNumber: setDict["phone"] = phoneNumber
        await self.db.updateOne({"_id": self.uid}, setDict=setDict, upsert=True)
        
    async def updateBusinessDetails(self, req: BusinessDetails):
        count, id = await self.db.updateOne({"_id": self.uid}, setDict=req.model_dump(mode="json", exclude_none=True))
        return SuccessResponse(success=count>0)
        
    async def deleteBusinessDetails(self):
        count, id = await self.db.updateOne({"_id": self.uid}, setDict={"businesstype": BusinessType.PERSONAL.value}, unsetFields=['business'])
        return SuccessResponse(success=count>0)
    
    async def isMarketplaceActive(self, id: str):
        try:
            marketplace = await self.client.db.marketplaces.getMarketplace(id)
            if marketplace.status==MarketplaceStatus.ACTIVE: return SuccessResponse(success=True)
            else: return SuccessResponse(success=False)
        except: return SuccessResponse(success=False)
    
    async def getUserAccounts(self):
        pipeline = [ { '$match': { '_id': self.uid } }, { '$lookup': { 'from': 'spapi_accounts', 'localField': '_id', 'foreignField': 'uid', 'pipeline': [ { '$project': { 'seller': 1, 'name': 1, 'sellerid': 1, 'countrycode': 1 } }, { '$lookup': { 'from': 'marketplaces', 'localField': 'sellerid', 'foreignField': 'sellerid', 'pipeline': [ { '$project': { 'storename': 1, 'countrycode': 1, 'marketplaceid': 1, 'profileid': 1, 'status': 1, 'uid': 1 } } ], 'as': 'marketplaces' } } ], 'as': 'spapi' } }, { '$set': { 'marketplaces': { '$reduce': { 'input': '$spapi', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$let': { 'vars': { 'spapi': '$$this' }, 'in': { '$reduce': { 'input': '$$spapi.marketplaces', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$mergeObjects': [ '$$this', { 'seller': { '_id': '$$spapi._id', 'name': '$$spapi.name', 'sellerid': '$$spapi.sellerid', 'countrycode': '$$spapi.countrycode' } } ] } ] ] } } } } } ] } } } } }, { '$set': { 'spapi': { '$map': { 'input': '$spapi', 'as': 's', 'in': { '$unsetField': { 'input': '$$s', 'field': 'marketplaces' } } } } } }, { '$lookup': { 'from': 'advertising_accounts', 'localField': '_id', 'foreignField': 'uid', 'pipeline': [ { '$project': { 'name': 1, 'countrycode': 1 } } ], 'as': 'ad' } }, { '$lookup': { 'from': 'subscriptions', 'localField': '_id', 'foreignField': '_id', 'pipeline': [ { '$replaceRoot': { 'newRoot': { 'status': '$status' } } } ], 'as': 'status' } }, { '$addFields': { 'status': { '$getField': { 'input': { '$first': '$status' }, 'field': 'status' } } } } ]
        data = await self.db.aggregate(pipeline)
        if len(data) == 0: raise ValueError("Not Found")
        return data[0]

    async def getUserBusinessWithActivePlanAndSubscriptionStatus(self):
        pipeline = [ { '$match': { '_id': self.uid } }, { '$lookup': { 'from': 'subscriptions', 'localField': 'subscription', 'foreignField': '_id', 'pipeline': [], 'as': 'subscription' } }, { '$set': { 'subscription': { '$first': '$subscription' } } }, { '$lookup': { 'from': 'pricing', 'localField': 'subscription.groupid', 'foreignField': '_id', 'let': { 'planid': '$subscription.planid' }, 'pipeline': [ { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$first': { '$filter': { 'input': '$plans', 'as': 'p', 'cond': { '$in': [ '$$planid', [ '$$p.amount.monthly.planid', '$$p.amount.yearly.planid' ] ] } } } } ] } } }, { '$project': { 'plans': 0, '_id': 0 } } ], 'as': 'plan' } }, { '$set': { 'plan': { '$first': '$plan' }, 'status': '$subscription.status' } }, { '$set': { 'duration': { '$reduce': { 'input': { '$objectToArray': '$plan.amount' }, 'initialValue': None, 'in': { '$cond': { 'if': { '$eq': [ '$$this.v.planid', '$subscription.planid' ] }, 'then': '$$this.k', 'else': '$$value' } } } } } }, { '$project': { 'business': 1, 'businesstype': 1, 'plan': 1, 'status': 1, 'duration': 1, '_id': 0 } } ]
        data = await self.db.aggregate(pipeline)
        if len(data)>0: return data[0]
        raise ValueError("User is not subscribed")


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
    

   