from datetime import datetime
from bson import ObjectId
from dzgroshared.db.collections.pipelines.marketplaces import GetUserMarketplaces
from dzgroshared.models.amazonapi.model import AmazonApiObject
from dzgroshared.models.collections.pg_orders import PGOrderCategory
from dzgroshared.models.collections.pricing import OfferType
from dzgroshared.models.enums import CollectionType, AmazonAccountType, CountryCode, MarketplaceId, MarketplaceStatus
from dzgroshared.models.model import AddMarketplaceRequest, Paginator, PyObjectId, StartEndDate, SuccessResponse
from dzgroshared.db import Exceptions
from dzgroshared.models.collections.marketplaces import Marketplace, MarketplaceCache, MarketplaceOnboardPaymentRequest, UserAccountsCount, MarketplaceNameId, UserMarketplaceList
from dzgroshared.models.collections.country_details import CountryDetailsWithBids
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.razorpay.common import CustomerKeys, RazorpayOrderObject
from dzgroshared.models.razorpay.order import RazorpayCreateOrder



class MarketplaceHelper:
    client: DzgroSharedClient
    db: DbManager
    spapiDB: DbManager
    advDb: DbManager

    def __init__(self, client: DzgroSharedClient):
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.MARKETPLACES.value), uid=self.client.uid)
        
    async def getMarketplace(self, id: str|ObjectId):
        marketplace = await self.db.findOne({'_id': self.db.convertToObjectId(id)})
        return Marketplace(**marketplace)

    async def getMarketplaceForCache(self, id: PyObjectId):
        return MarketplaceCache.model_validate(self.db.findOne({"_id": id, "uid": self.client.uid}, projectionInc=["sellerid", "profileid", "marketplaceid","countrycode","uid"]))
    
    async def getMarketplaceObjectForReport(self, marketplace: ObjectId):
        from dzgroshared.db.collections.pipelines.marketplaces import MarketplaceObjectForReport
        pipeline = MarketplaceObjectForReport.pipeline(marketplace, self.client.uid)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Marketplace")
        return data[0]
        
    
    async def completeReportProcessing(self, id:str|ObjectId, dates: StartEndDate, lastrefresh: datetime, lastreport: ObjectId):
        await self.db.updateOne({"_id": self.db.convertToObjectId(id)}, setDict={"dates":dates.model_dump(), "lastrefresh": lastrefresh, "lastreport": lastreport, "status": MarketplaceStatus.ACTIVE.value})

        
    async def getMarketplaceApiObject(self, id: str|ObjectId, client_id:str, client_secret:str, accountType: AmazonAccountType):
        collection: CollectionType = CollectionType.SPAPI_ACCOUNTS if accountType==AmazonAccountType.SPAPI else CollectionType.ADVERTISING_ACCOUNTS
        urlKey = '$spapi_url' if accountType==AmazonAccountType.SPAPI else '$ad_url'
        objKey = 'seller' if accountType==AmazonAccountType.SPAPI else 'ad'
        pipeline = [ 
            self.db.pp.matchMarketplace({'_id': self.db.convertToObjectId(id)}),
            self.db.pp.lookup(collection, 'result', localField=objKey, foreignField='_id', pipeline=[ { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken" } } ]),
            self.db.pp.replaceRoot(self.db.pp.mergeObjects([{ '$first': '$result' }, { 'marketplaceid': '$marketplaceid', 'profile': '$profileid', 'region': '$region' }])) ]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        return AmazonApiObject(**{**data[0], 'client_id': client_id, 'client_secret': client_secret, "isad": accountType==AmazonAccountType.ADVERTISING})

    async def getCountryBidsByMarketplace(self, id: ObjectId|str)->CountryDetailsWithBids:
        pp = self.db.pp
        matchStage = pp.match({"_id": self.db.convertToObjectId(id), "uid": self.client.uid})
        lookupDetail = pp.lookup(CollectionType.COUNTRY_DETAILS, "detail", localField="countrycode", foreignField="_id")
        unwind = pp.unwind("detail")
        replaceWith = pp.replaceRoot("$detail")
        res = await self.db.aggregate([matchStage, lookupDetail, unwind, replaceWith])
        return CountryDetailsWithBids(**res[0])

    
    async def lookbackPeriod(self, id: ObjectId|str)->int:
        pp = self.db.pp
        matchStage = pp.match({"_id": self.db.convertToObjectId(id), "uid": self.client.uid})
        setlookback = pp.replaceWith( { 'lookback': { '$dateDiff': { 'startDate': '$startDate', 'endDate': '$endDate', 'unit': 'day' } } } )
        return (await self.db.aggregate([matchStage, setlookback]))[0]['lookback']

    
    async def getMarketplaceWithToken(self, id: str|ObjectId):
        pp = self.db.pp
        matchStage = pp.match({"_id": self.db.convertToObjectId(id), "uid": self.client.uid})
        lookupDetail = pp.lookup(CollectionType.COUNTRY_DETAILS, "detail", localField="countryCode", foreignField="_id", pipeline=[pp.project([],["_id"])])
        lookupSpapi = pp.lookup(CollectionType.SPAPI_ACCOUNTS, "spapi", localField="seller", foreignField="_id")
        lookupAdv = pp.lookup(CollectionType.AD_ACCOUNTS, "adAccount", localField="adAccount", foreignField="_id")
        unwind = pp.unwind("detail")
        setaccounts = pp.set({ 'spapi': { '$first': '$spapi' }, 'adAccount': { '$first': '$adAccount' } })
        lookupadvertisingAccount = pp.lookup(CollectionType.ADVERTISING_ACCOUNTS, "advertisingAccount", localField="adAccount.advertisingAccount", foreignField="_id")
        setAdvertisingAccount = pp.set({ 'advertisingAccount': { '$first': '$advertisingAccount' } })
        pipeline = [matchStage, lookupDetail, lookupSpapi, lookupAdv, unwind, setaccounts, lookupadvertisingAccount, setAdvertisingAccount]
        result = list(await self.db.aggregate(pipeline))
        if len(result)==0: raise ValueError("Marketplace could not be found")
        return result[0]

    async def getUserAccountsCount(self)->UserAccountsCount:
        spapiAccountsCount = await self.spapiDB.count({"uid": self.client.uid})
        advertisingAccountsCount = await self.advDb.count({"uid": self.client.uid})
        return UserAccountsCount(spapiAccountsCount=spapiAccountsCount, advertisingAccountsCount=advertisingAccountsCount)

    async def getAllMarketplaceNames(self, uid: str)->list[MarketplaceNameId]:
        res = await self.db.find({"uid": uid}, projectionInc=["name"] )
        return [MarketplaceNameId(**x) for x in res]

    async def getTeamMemberMarketplaces(self, ids: list[str])->list[MarketplaceNameId]:
        res = await self.db.find({"uid": self.client.uid, "_id": {"$in": [ObjectId(id) for id in ids]}}, projectionInc=["name"] )
        return [MarketplaceNameId(**x) for x in res]

    async def getMarketplaces(self, paginator: Paginator):
        pipeline = GetUserMarketplaces.pipeline(self.client.uid, paginator)
        data = await self.db.aggregate(pipeline)
        count: int|None = None
        if paginator.skip==0:
            count = await self.db.count({"uid": self.client.uid})
            if count==0: raise Exceptions.MISSING_MARKETPLACE
        count = None if paginator.skip!=0 else await self.db.count({"uid": self.client.uid})
        return UserMarketplaceList.model_validate({"data": data, "count": count})
    
    async def getPlanDetails(self, marketplaceid:PyObjectId, planid:str):
        client = await self.client.db.spapi_accounts.getAccountApiClient(marketplaceid)
        res = await client.sales.getLast30DaysSales()
        sales = float(res.payload[0].total_sales.amount) if res.payload else 0
        return await self.client.db.pricing.getPlanDetailItemsById(planid, sales)

    async def getAllMarketplaceIdsBySellerIdForUser(self, sellerId: str)->list[str]:
        ids = await self.db.find({"uid": self.client.uid, "sellerId": sellerId}, projectionInc=["marketplaceId"])
        return [id['marketplaceId'] for id in ids]
    
    async def addMarketplaces(self, sellerid: str, marketplaces: list[MarketplaceId]):
        data: list[dict] = [{sellerid: "sellerid", "uid": self.client.uid} for marketplace in marketplaces]
        await self.db.insertMany(data)

    async def getMarketplaceById(self, id: PyObjectId):
        return await self.db.findOne({"_id": id})
    
    async def testLinkage(self, req: AddMarketplaceRequest):
        spClient = await self.client.db.spapi_accounts.getAccountApiClient(req.seller)
        adClient = await self.client.db.advertising_accounts.getAccountApiClient(req.ad)
        listings = await spClient.listings.search_listings_items(
            seller_id=req.sellerid, 
            included_data=['summaries']
        )
        if not listings.items: raise ValueError("No listings found for the seller")
        listing = listings.items[0]
        asin = next((summary.asin for summary in listing.summaries if summary.marketplace_id==req.marketplaceid.value), None) if listing.summaries else None
        if not asin: return SuccessResponse(success=False, message="Selected Marketplace has no active products")
        from dzgroshared.amazonapi.adapi.common.products import ProductMetadataRequest
        metadata = await adClient.common.productsMetadataClient.listProducts(
            ProductMetadataRequest(skus=[listing.sku], pageIndex=0, pageSize=1)
        )
        if metadata.ProductMetadataList and metadata.ProductMetadataList[0].asin == asin: return SuccessResponse(success=True)
        return SuccessResponse(success=False, message="Selected Ad Account and Marketplace do not belong to same seller account")

    async def addMarketplace(self, req: AddMarketplaceRequest):
        data = await self.client.db.spapi_accounts.getMarketplaceParticipations(req.seller)
        if not any(marketplace.marketplace.id==req.marketplaceid.value for marketplace in data.data):
            raise ValueError("Marketplace not found for the given seller")
        data = req.model_dump(mode="json")
        data.update({"seller": req.seller, "ad": req.ad, "status": MarketplaceStatus.NEW.value})
        id = await self.db.insertOne(data)
        return SuccessResponse(success=True)
    
    def createRazorpayOrderObject(self, orderId: str, name: str, email:str, phonenumber: str|None=None)->RazorpayOrderObject:
        readonlyKeys:dict[CustomerKeys,bool] = {'name': True, 'email': True, 'contact': False}
        prefill:dict[CustomerKeys,str] = {'name': name, 'email': email}
        if phonenumber: 
            prefill['contact'] = phonenumber
            readonlyKeys['contact'] = True
        return RazorpayOrderObject(order_id=orderId, prefill=prefill, key=self.client.secrets.RAZORPAY_CLIENT_ID, readonly=readonlyKeys)
    
    
    async def generateOrderForOnboarding(self, req: MarketplaceOnboardPaymentRequest):
        plan = await self.getPlanDetails(req.id, req.planid)
        amount = plan.total
        orderReq = RazorpayCreateOrder( 
            amount=int(amount*100),
            receipt=str(req.id),
            notes={ "uid": self.client.uid, "marketplace": str(req.id) } )
        order = await self.client.razorpay.order.create_order(orderReq)
        await self.client.db.pg_orders.addOrder(order, category=PGOrderCategory.MARKETPLACE_ONBOARDING, marketplace=req.id)
        return self.createRazorpayOrderObject(order.id, self.client.user.name, self.client.user.email, self.client.user.phoneNumber)



    
