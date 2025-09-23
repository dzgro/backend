from datetime import datetime, timedelta
from bson import ObjectId
from dzgroshared.analytics import controller
from dzgroshared.analytics.model import KEY_METRICS
from dzgroshared.db.marketplaces.pipelines import GetMarketplaceObjectForReport, GetPeriodData, GetUserMarketplaces
from dzgroshared.amazonapi.model import AmazonApiObject
from dzgroshared.db.pricing.model import OfferType, Pricing
from dzgroshared.db.enums import CollateType, CollectionType, AmazonAccountType, CountryCode, MarketplaceId, MarketplaceStatus, PlanType
from dzgroshared.db.model import AddMarketplaceRequest, Paginator, PeriodDataRequest, PeriodDataResponse, PyObjectId, StartEndDate, SuccessResponse
from dzgroshared.db.marketplaces.model import DashboardData, Marketplace, MarketplaceCache, MarketplaceObjectForReport, MarketplaceOnboardPaymentRequest, UserAccountsCount, MarketplaceNameId, UserMarketplace, UserMarketplaceList
from dzgroshared.db.country_details.model import CountryDetailsWithBids
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.razorpay.common import CustomerKeys, RazorpayOrderObject
from dzgroshared.razorpay.order.model import RazorpayCreateOrder
from dzgroshared.db.razorpay_orders.model import  RazorPayDbOrderCategory

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
    
    async def getMarketplacePricingId(self, id: PyObjectId)->PyObjectId:
        return (await self.db.findOne({'_id': id}, projectionInc=['pricing']))['pricing']
    
    async def getMarketplaceStatus(self, id: PyObjectId):
        return MarketplaceStatus((await self.db.findOne({'_id': id}, projectionInc=['status']))['status'])
    
    async def startMarketplaceReporting(self, id: PyObjectId, plantype: PlanType):
        status = await self.getMarketplaceStatus(id)
        if status != MarketplaceStatus.NEW: raise ValueError("Marketplace is already onboarded")
        count, updatedId  = await self.db.updateOne({"_id": id}, setDict={"status": MarketplaceStatus.BUFFERING.value, "plantype": plantype.value})
        if count==0: raise ValueError("Marketplace could not be updated")
        from dzgroshared.sqs.model import SendMessageRequest, QueueName
        from dzgroshared.db.queue_messages.model import AmazoMarketplaceDailyReportQM, AmazonDailyReportAggregationStep
        req = SendMessageRequest(Queue=QueueName.AMAZON_REPORTS)
        body = AmazoMarketplaceDailyReportQM(marketplace=id, step=AmazonDailyReportAggregationStep.CREATE_REPORTS, uid=self.client.uid)
        await self.client.sqs.sendMessage(req, body)

    async def getMarketplaceForCache(self, id: PyObjectId):
        return MarketplaceCache.model_validate(self.db.findOne({"_id": id, "uid": self.client.uid}, projectionInc=["sellerid", "profileid", "marketplaceid","countrycode","uid"]))
    
    async def getMarketplaceObjectForReport(self, marketplace: PyObjectId):
        pipeline = GetMarketplaceObjectForReport.pipeline(marketplace, self.client.uid)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Marketplace")
        return MarketplaceObjectForReport.model_validate(data[0])
    
    
    async def getPeriodData(self, req: PeriodDataRequest):
        pipeline = GetPeriodData.pipeline(self.client.uid, self.client.marketplaceId, req)
        data = await self.db.aggregate(pipeline)
        return PeriodDataResponse.model_validate({"data": controller.transformData('Period',data, req.collatetype, self.client.marketplace.countrycode)})
    
    async def completeReportProcessing(self, id:str|ObjectId, dates: StartEndDate, lastrefresh: datetime, lastreport: ObjectId):
        await self.db.updateOne({"_id": self.db.convertToObjectId(id)}, setDict={"dates":dates.model_dump(), "lastrefresh": lastrefresh, "lastreport": lastreport, "status": MarketplaceStatus.ACTIVE.value})

        
    async def getMarketplaceApiObject(self, id: str|ObjectId, accountType: AmazonAccountType):
        collection: CollectionType = CollectionType.SPAPI_ACCOUNTS if accountType==AmazonAccountType.SPAPI else CollectionType.ADVERTISING_ACCOUNTS
        urlKey = '$spapi_url' if accountType==AmazonAccountType.SPAPI else '$ad_url'
        objKey = 'seller' if accountType==AmazonAccountType.SPAPI else 'ad'
        pipeline = [ 
            self.db.pp.matchMarketplace({'_id': self.db.convertToObjectId(id)}),
            self.db.pp.lookup(collection, 'result', localField=objKey, foreignField='_id', pipeline=[ { '$lookup': { 'from': 'country_details', 'localField': 'countrycode', 'foreignField': '_id', 'pipeline': [ { '$project': { 'url': urlKey, '_id': 0 } } ], 'as': 'url' } }, { '$unwind': { 'path': '$url' } }, { '$replaceWith': { '_id': '$_id', 'sellerid': '$sellerid', 'url': '$url.url', "refreshtoken": "$refreshtoken" } } ]),
            self.db.pp.replaceRoot(self.db.pp.mergeObjects([{ '$first': '$result' }, { 'marketplaceid': '$marketplaceid', 'profile': '$profileid', 'region': '$region' }])) ]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Invalid Seller Configuration")
        client_id = self.client.secrets.SPAPI_CLIENT_ID if accountType==AmazonAccountType.SPAPI else self.client.secrets.ADS_CLIENT_ID
        client_secret = self.client.secrets.SPAPI_CLIENT_SECRET if accountType==AmazonAccountType.SPAPI else self.client.secrets.ADS_CLIENT_SECRET
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
            if count==0: raise ValueError("No Marketplaces found for the user")
        count = None if paginator.skip!=0 else await self.db.count({"uid": self.client.uid})
        return UserMarketplaceList.model_validate({"data": data, "count": count})

    async def getUserMarketplace(self):
        pipeline = GetUserMarketplaces.pipeline(self.client.uid, Paginator(skip=0, limit=1), self.client.marketplaceId)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Marketplace found for the user")
        return UserMarketplace.model_validate(data[0])

    async def getPlans(self, id: PyObjectId):
        pipeline = [ {"$match": {"_id": id}}, { '$lookup': { 'from': 'pricing', 'localField': 'pricing', 'foreignField': '_id', 'as': 'pricing' } }, { '$replaceRoot': { 'newRoot': { '$first': '$pricing' } } } ]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Pricing found")
        return Pricing.model_validate(data[0])
    
    async def getPlanDetails(self, marketplaceid:PyObjectId):
        obj = await self.getMarketplaceApiObject(marketplaceid, AmazonAccountType.SPAPI)
        from dzgroshared.amazonapi.spapi import SpApiClient
        client = SpApiClient(obj)
        res = await client.sales.getLast30DaysSales()
        sales = float(res.payload[0].total_sales.amount) if res.payload else 0
        pricing = await self.getMarketplacePricingId(marketplaceid)
        return await self.client.db.pricing.getPlanDetailItemsById(pricing, sales)

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
        spClient.object.marketplaceid = req.marketplaceid.value
        adClient = await self.client.db.advertising_accounts.getAccountApiClient(req.ad)
        adClient.object.profile = req.profileid
        listings = await spClient.listings.search_listings_items(
            seller_id=req.sellerid, 
            included_data=['summaries']
        )
        if not listings.items: raise ValueError("No listings found for the seller")
        listing = listings.items[0]
        asin = next((summary.asin for summary in listing.summaries if summary.marketplace_id==req.marketplaceid.value), None) if listing.summaries else None
        if not asin: return SuccessResponse(success=False, message="Selected Marketplace has no active products")
        from dzgroshared.amazonapi.adapi.common.products.model import ProductMetadataRequest
        metadata = await adClient.common.productsMetadataClient.listProducts(
            ProductMetadataRequest(skus=[listing.sku], pageIndex=0, pageSize=1)
        )
        if metadata.ProductMetadataList and metadata.ProductMetadataList[0].asin == asin: return SuccessResponse(success=True)
        return SuccessResponse(success=False, message="Selected Ad Account and Marketplace do not belong to same seller account")

    async def addMarketplace(self, req: AddMarketplaceRequest):
        data = await self.client.db.spapi_accounts.getMarketplaceParticipations(req.seller)
        if not any(marketplace.marketplaceid==req.marketplaceid.value for marketplace in data.data):
            raise ValueError("Marketplace not found for the given seller")
        data = req.model_dump(mode="json")
        pricingid = await self.client.db.pricing.getActivePlanId(req.countrycode)
        data.update({"seller": req.seller, "ad": req.ad, "status": MarketplaceStatus.NEW.value, "pricing": pricingid})
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
        status = await self.getMarketplaceStatus(req.id)
        if status != MarketplaceStatus.NEW: raise ValueError("Marketplace is already onboarded")
        planDetails = await self.getPlanDetails(req.id)
        plan = next((plan for plan in planDetails.plans if plan.plantype==req.plantype), None)
        if not plan: raise ValueError("Plan not found")
        orderReq = RazorpayCreateOrder( 
            amount=int(plan.total*100),
            receipt=str(req.id),
            notes={ "uid": self.client.uid, "marketplace": str(req.id), "plantype": req.plantype.value, "pricing": str(req.pricing) } )
        order = await self.client.razorpay.order.create_order(orderReq)
        await self.client.db.razorpay_orders.addOrder(order, category=RazorPayDbOrderCategory.MARKETPLACE_ONBOARDING)
        return self.createRazorpayOrderObject(order.id, self.client.user.name, self.client.user.email, self.client.user.phone_number)
    
    async def getMonths(self):
        def last_day_of_month(year: int, month: int) -> int:
            if month == 12:next_month = datetime(year + 1, 1, 1)
            else:next_month = datetime(year, month + 1, 1)
            return (next_month - timedelta(days=1)).day
        marketplace = await self.client.db.marketplaces.getMarketplace(self.client.marketplaceId)
        year, month = marketplace.dates.startdate.year, marketplace.dates.startdate.month
        end_year, end_month = marketplace.dates.enddate.year, marketplace.dates.enddate.month
        results = []
        while (year, month) <= (end_year, end_month):
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, last_day_of_month(year, month))
            range_start = max(first_day, marketplace.dates.startdate)
            range_end = min(last_day, marketplace.dates.enddate)
            results.append({
                "month": first_day.strftime("%b %Y"),
                "period": f"{range_start.strftime('%d %b')} - {range_end.strftime('%d %b')}",
                "startdate": range_start,
                "enddate": range_end
            })
            month += 1
            if month > 12:
                month = 1
                year += 1
        return results
    
    async def getDashboardData(self, collatetype: CollateType, value: str|None=None):
        from dzgroshared.db.marketplaces.pipelines import DataDashboard
        keys = [y.metric.value for x in KEY_METRICS for y in x.items]
        pipeline = DataDashboard.pipeline(self.db.pp, self.client.marketplaceId, collatetype, value, keys)
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        marketplaces = await self.db.aggregate(pipeline)
        data = marketplaces[0]
        data['periods'] = controller.transformData('Period',data['periods'], collatetype, self.client.marketplace.countrycode)
        data['states'] = controller.transformData('State Lite',data['states'], collatetype, self.client.marketplace.countrycode)
        data['performance'] = controller.transformData('Comparison',data['performance'], collatetype, self.client.marketplace.countrycode)
        monthMeterGroups = controller.transformData('Month Meters',data['months'], collatetype, self.client.marketplace.countrycode)
        monthBars = controller.transformData('Month Bars',data['months'], collatetype, self.client.marketplace.countrycode)
        monthdata = controller.transformData('Month Data',data['months'], collatetype, self.client.marketplace.countrycode)
        data['months'] = [{**month, "meterGroups": monthMeterGroups[i]['data'] if len(monthMeterGroups)>i and 'data' in monthMeterGroups[i] else [], "bars": monthBars[i]['data'][0] if len(monthBars)>i and 'data' in monthBars[i] and len(monthBars[i]['data'])>0 else [], "data": monthdata[i]['data'][0] if len(monthdata)>i and 'data' in monthdata[i] and len(monthdata[i]['data'])>0 else []} for i, month in enumerate(data['months'])]
        data['keys'] = controller.transformData('Key Metrics', data['keys'],collatetype, self.client.marketplace.countrycode)
        data =  {"collatetype": collatetype.value, "value": value, **data}
        try:
            return DashboardData.model_validate(data)
        except Exception as e:
            print(e)
            print(data)

    
