from datetime import datetime
from bson import ObjectId
from dzgroshared.models.amazonapi.model import AmazonApiObject
from dzgroshared.models.enums import CollectionType, AmazonAccountType, CountryCode, MarketplaceId, MarketplaceStatus
from dzgroshared.models.model import Paginator, SuccessResponse, AddMarketplace
from dzgroshared.db import Exceptions
from dzgroshared.models.collections.marketplaces import Marketplace, UserAccountsCount, MarketplaceNameId, Account, AdAccount, RenameAccountRequest
from dzgroshared.db.collections.pipelines import GetAdAccounts, GetMarketplaces
from dzgroshared.models.collections.country_details import CountryDetailsWithBids
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient



class MarketplaceHelper:
    uid:str
    marketplaceDB: DbManager
    spapiDB: DbManager
    advDb: DbManager

    def __init__(self, client: DzgroSharedClient, uid:str):
        self.uid = uid
        self.marketplaceDB = DbManager(client.db.database.get_collection(CollectionType.MARKETPLACES.value), uid=self.uid)
        self.spapiDB = DbManager(client.db.database.get_collection(CollectionType.SPAPI_ACCOUNTS.value), uid=self.uid)
        self.advDb = DbManager(client.db.database.get_collection(CollectionType.ADVERTISING_ACCOUNTS.value), uid=self.uid)

    async def getMarketplace(self, id: str|ObjectId):
        marketplace = await self.marketplaceDB.findOne({'_id': self.marketplaceDB.convertToObjectId(id)})
        return Marketplace(**marketplace)
    
    async def getMarketplaceObjectForReport(self, marketplace: ObjectId):
        from dzgroshared.db.collections.pipelines.marketplaces import MarketplaceObjectForReport
        pipeline = MarketplaceObjectForReport.pipeline(marketplace, self.uid)
        data = await self.marketplaceDB.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Marketplace")
        return data[0]
        
    
    async def completeReportProcessing(self, id:str|ObjectId, startdate: datetime, enddate: datetime, lastrefresh: datetime, lastreport: ObjectId):
        await self.marketplaceDB.updateOne({"_id": self.marketplaceDB.convertToObjectId(id)}, setDict={"startdate":startdate, "enddate": enddate, "lastrefresh": lastrefresh, "lastreport": lastreport, "status": MarketplaceStatus.ACTIVE.value})

    async def addMarketplace(self, body: AddMarketplace):
        data = body.model_dump(mode="json")
        data.update({"seller": ObjectId(body.seller), "ad": ObjectId(body.ad), "status": MarketplaceStatus.NEW.value})
        await self.marketplaceDB.insertOne(data, withUidMarketplace=True)
        
    async def getMarketplaceApiObject(self, id: str|ObjectId, client_id:str, client_secret:str, accountType: AmazonAccountType):
        collection: CollectionType = CollectionType.SPAPI_ACCOUNTS if accountType==AmazonAccountType.SPAPI else CollectionType.ADVERTISING_ACCOUNTS
        urlKey = '$spapi_url' if accountType==AmazonAccountType.SPAPI else '$ad_url'
        objKey = 'seller' if accountType==AmazonAccountType.SPAPI else 'ad'
        pipeline = [ 
            self.marketplaceDB.pp.matchMarketplace({'_id': self.marketplaceDB.convertToObjectId(id)}),
            self.marketplaceDB.pp.lookup(collection, 'result', localField=objKey, foreignField='_id', pipeline=[ { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken" } } ]),
            self.marketplaceDB.pp.replaceRoot(self.marketplaceDB.pp.mergeObjects([{ '$first': '$result' }, { 'marketplaceid': '$marketplaceid', 'profile': '$profileid', 'region': '$region' }])) ]
        data = await self.marketplaceDB.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        return AmazonApiObject(**{**data[0], 'client_id': client_id, 'client_secret': client_secret, "isad": accountType==AmazonAccountType.ADVERTISING})

    async def getCountryBidsByMarketplace(self, id: ObjectId|str)->CountryDetailsWithBids:
        pp = self.marketplaceDB.pp
        matchStage = pp.match({"_id": self.marketplaceDB.convertToObjectId(id), "uid": self.uid})
        lookupDetail = pp.lookup(CollectionType.COUNTRY_DETAILS, "detail", localField="countrycode", foreignField="_id")
        unwind = pp.unwind("detail")
        replaceWith = pp.replaceRoot("$detail")
        res = await self.marketplaceDB.aggregate([matchStage, lookupDetail, unwind, replaceWith])
        try:
            return CountryDetailsWithBids(**res[0])
        except Exception as e:
            print(e.args[0])
            raise Exception

    
    async def lookbackPeriod(self, id: ObjectId|str)->int:
        pp = self.marketplaceDB.pp
        matchStage = pp.match({"_id": self.marketplaceDB.convertToObjectId(id), "uid": self.uid})
        setlookback = pp.replaceWith( { 'lookback': { '$dateDiff': { 'startDate': '$startDate', 'endDate': '$endDate', 'unit': 'day' } } } )
        return (await self.marketplaceDB.aggregate([matchStage, setlookback]))[0]['lookback']

    
    async def getMarketplaceWithToken(self, id: str|ObjectId):
        pp = self.marketplaceDB.pp
        matchStage = pp.match({"_id": self.marketplaceDB.convertToObjectId(id), "uid": self.uid})
        lookupDetail = pp.lookup(CollectionType.COUNTRY_DETAILS, "detail", localField="countryCode", foreignField="_id", pipeline=[pp.project([],["_id"])])
        lookupSpapi = pp.lookup(CollectionType.SPAPI_ACCOUNTS, "spapi", localField="seller", foreignField="_id")
        lookupAdv = pp.lookup(CollectionType.AD_ACCOUNTS, "adAccount", localField="adAccount", foreignField="_id")
        unwind = pp.unwind("detail")
        setaccounts = pp.set({ 'spapi': { '$first': '$spapi' }, 'adAccount': { '$first': '$adAccount' } })
        lookupadvertisingAccount = pp.lookup(CollectionType.ADVERTISING_ACCOUNTS, "advertisingAccount", localField="adAccount.advertisingAccount", foreignField="_id")
        setAdvertisingAccount = pp.set({ 'advertisingAccount': { '$first': '$advertisingAccount' } })
        pipeline = [matchStage, lookupDetail, lookupSpapi, lookupAdv, unwind, setaccounts, lookupadvertisingAccount, setAdvertisingAccount]
        result = list(await self.marketplaceDB.aggregate(pipeline))
        if len(result)==0: raise ValueError("Marketplace could not be found")
        return result[0]

    async def getUserAccountsCount(self)->UserAccountsCount:
        spapiAccountsCount = await self.spapiDB.count({"uid": self.uid})
        advertisingAccountsCount = await self.advDb.count({"uid": self.uid})
        return UserAccountsCount(spapiAccountsCount=spapiAccountsCount, advertisingAccountsCount=advertisingAccountsCount)

    async def getAllMarketplaceNames(self, uid: str)->list[MarketplaceNameId]:
        res = await self.marketplaceDB.find({"uid": uid}, projectionInc=["name"] )
        return [MarketplaceNameId(**x) for x in res]

    async def getTeamMemberMarketplaces(self, ids: list[str])->list[MarketplaceNameId]:
        res = await self.marketplaceDB.find({"uid": self.uid, "_id": {"$in": [ObjectId(id) for id in ids]}}, projectionInc=["name"] )
        return [MarketplaceNameId(**x) for x in res]

    async def getMarketplaces(self)->list[dict]:
        pipeline = GetMarketplaces.pipeline(self.uid)
        data = await self.spapiDB.aggregate(pipeline)
        return data
        
    async def getAllMarkeptlaceIdsBySellerIdForUser(self, sellerId: str)->list[str]:
        ids = await self.marketplaceDB.find({"uid": self.uid, "sellerId": sellerId}, projectionInc=["marketplaceId"])
        return [id['marketplaceId'] for id in ids]
    
    async def updateSeller(self, sellerId: str, updateDict: dict, upsert: bool=False):
       await self.spapiDB.updateOne({"sellerId": sellerId, "uid": self.uid}, updateDict, upsert=upsert)
    
    async def addAdvertisingAccount(self, refreshtoken: str, countryCode: CountryCode, name: str):
        data = {"name": name, "uid": self.uid, "countrycode": countryCode, "refreshtoken": refreshtoken}
        data.update()
        id =  await self.advDb.insertOne(data)
        return await self.getAdvertisingAccount(str(id))
    
    async def deleteAdvertisingAccount(self, id: str):
        await self.advDb.deleteOne({"_id": ObjectId(id), "uid": self.uid})
    

    async def addMarketplaces(self, sellerid: str, marketplaces: list[MarketplaceId]):
        data: list[dict] = [{sellerid: "sellerid", "uid": self.uid} for marketplace in marketplaces]
        await self.marketplaceDB.insertMany(data)
    
    async def getMarketplaceById(self, id: str|ObjectId):
        marketplace =  await self.marketplaceDB.findOne({"_id": self.marketplaceDB.convertToObjectId(id)})
        if not marketplace: raise Exceptions.MISSING_MARKETPLACE
        return marketplace

    async def isSellerAlreadyAdded(self, sellerId: str)->bool:
        seller = await self.spapiDB.findOne({"sellerId": sellerId, "uid": self.uid})
        if not seller: return False
        return True

    async def getAdvertisingAccount(self, id: str|ObjectId)->Account:
        account = await self.advDb.findOne({"_id": self.marketplaceDB.convertToObjectId(id), "uid": self.uid})
        if not account: raise Exceptions.MISSING_ADVERISING_ACCOUNT
        return Account(**account)

    async def listAdvertisingAccounts(self, paginator: Paginator, id: str|None=None)->list[dict]:
        pipeline = GetAdAccounts.pipeline(self.uid, paginator, id)
        accounts = list(await self.advDb.aggregate(pipeline))
        return accounts
    
    async def renameAccount(self, body: RenameAccountRequest):
        collection = self.spapiDB if body.accountType==AmazonAccountType.SPAPI else self.advDb
        count = await collection.updateOne({"_id": ObjectId(body.id)}, setDict={"name": body.name})
        return SuccessResponse(success=count[0]>0)
    
    async def getAdAccount(self, id: str):
        res = await self.advDb.findOne({"_id": ObjectId(id)})
        if not res: raise ValueError("Ad Account could not be found")
        return AdAccount(**res)
    
    async def updateMarketplaceStartDate(self, id: ObjectId, startDate: datetime):
        count = await self.marketplaceDB.updateOne({"_id": id, "startDate": {"$exists": False}}, {"$set": {"startDate": startDate}})
        if count[0]>0: return startDate

    
