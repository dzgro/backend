from amazon_daily_report.reports.ReportUtils import ReportUtil
from amazon_daily_report.reports.report_types.adexport.AdsExportApp import AmazonAdsExportManager, AmazonExportReport
from amazon_daily_report.reports.report_types.datakiosk.DataKioskReportApp import AmazonDataKioskReportManager
from amazonapi import AmazonApiClient
from amazonapi.adapi import AdApiClient
from amazonapi.spapi import SpApiClient
from db import DbClient
from bson import ObjectId
from db.collections.amazon_daily_reports import AmazonDailyReportHelper
from db.collections.products import ProductHelper
from db.collections.queue_messages import QueueMessagesHelper
from models.collections.queue_messages import AmazonParentReportQueueMessage
from models.enums import AdAssetType, AmazonAccountType, AmazonDailyReportAggregationStep, AmazonReportType, CollectionType, QueueUrl, SQSMessageStatus
from models.extras.amazon_daily_report import AmazonAdReport, AmazonDataKioskReport, AmazonParentReport, MarketplaceObjectForReport, AmazonSpapiReport
from date_util import DateHelper
from models.model import LambdaContext, MockLambdaContext
from sqs import SqsHelper
from amazon_daily_report.reports.report_types.spapi.SpapiReportApp import AmazonSpapiReportManager
from amazon_daily_report.reports.report_types.adexport.AdsExportApp import AmazonAdsExportManager
from amazon_daily_report.reports.report_types.datakiosk.DataKioskReportApp import AmazonDataKioskReportManager
from amazon_daily_report.reports.report_types.ad.AdsReportApp import AmazonAdsReportManager
from sqs.model import SendMessageRequest
from dzgrosecrets import SecretManager

class AmazonReportManager:
    userMarketplace: MarketplaceObjectForReport
    sqs: SqsHelper
    sqsDb: QueueMessagesHelper
    reportsDb: AmazonDailyReportHelper
    productsDb: ProductHelper
    spapiReportManager: AmazonSpapiReportManager
    dataKioskReportManager: AmazonDataKioskReportManager
    adReportManager: AmazonAdsReportManager
    adExportManager: AmazonAdsExportManager
    helper: DateHelper
    report: AmazonParentReport
    spapi: SpApiClient
    adApi: AdApiClient
    secrets: SecretManager

    def __init__(self, messageId: str, message: AmazonParentReportQueueMessage, context: LambdaContext|MockLambdaContext) -> None:
        self.messageId = messageId
        self.context = context
        self.message = message
        self.helper = DateHelper()
        self.sqsDb = self.getDb().sqs_messages()
        self.reportsDb = self.getDb().amazon_daily_reports(self.message.uid, self.message.marketplace)
        self.productsDb = self.getDb().products(self.message.uid, self.message.marketplace)
        self.secrets = SecretManager()

    def __getattr__(self, item):
        return None
    
    async def checkMessage(self):
        try:
            dbMessageStatus = await self.sqsDb.getMessageStatus(self.messageId)
            if dbMessageStatus==SQSMessageStatus.PENDING: 
                await self.sqsDb.setMessageAsProcessing(self.messageId)
                
                return await self.executeMessage()
            return None
        except Exception as e:
            error = e.args[0] if len(e.args)>0 else "Some error Occurred"
            await self.sqsDb.setMessageAsFailed(self.messageId, error)
            await self.reportsDb.terminateParent(self.report.id, error)
    
    async def setUserMarketplace(self):
        self.userMarketplace = MarketplaceObjectForReport(**await self.getDb().marketplaces(self.message.uid).getMarketplaceObjectForReport(ObjectId(self.message.marketplace)))
        self.userMarketplace.spapi.client_id = self.secrets.SPAPI_CLIENT_ID
        self.userMarketplace.spapi.client_secret = self.secrets.SPAPI_CLIENT_SECRET
        self.userMarketplace.ad.client_id = self.secrets.ADS_CLIENT_ID
        self.userMarketplace.ad.client_secret = self.secrets.ADS_CLIENT_SECRET

    async def executeMessage(self)->tuple[AmazonParentReportQueueMessage, str]|None:
        if not self.message.index:
            if self.message.step==AmazonDailyReportAggregationStep.CREATE_REPORTS:
                return await self.createReports()
        else:
            reportid = ObjectId(self.message.index)
            self.report = await self.reportsDb.getParentReport(reportid)
            if self.message.step==AmazonDailyReportAggregationStep.ADD_PRODUCTS:
                from amazon_daily_report.reports.AddProducts import ListingsBuilder
                builder = ListingsBuilder(self.userMarketplace, self.context, await self.getSpapiClient(), self.getDb(), ReportUtil(self.userMarketplace), self.report.id)
                self.message.date = await builder.execute(self.message.date)
                if self.message.date: return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PRODUCTS)
                else:
                    await self.reportsDb.markProductsComplete(reportid)
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS)
            elif self.message.step==AmazonDailyReportAggregationStep.PROCESS_REPORTS: 
                if self.report.progress!=100: 
                    await self.processReports()
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.PROCESS_REPORTS, delay=10)
                else:
                    await self.reportsDb.markReportsComplete(reportid)
                    # if self.report.productsComplete: return self.sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS)
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS)
            elif self.message.step==AmazonDailyReportAggregationStep.ADD_PORTFOLIOS:
                if not self.report.productsComplete or self.report.progress!=100:
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS, delay=60)
                else:
                    from amazon_daily_report.reports.pipelines.AddPortfolios import PortfolioProcessor
                    portfolios = await PortfolioProcessor(self.userMarketplace, await self.getAdApiClient()).getPortfolios()
                    await ReportUtil(self.userMarketplace).update(self.getDb(), CollectionType.ADV_ASSETS, portfolios, self.report.id)
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_ADS)
            elif self.message.step==AmazonDailyReportAggregationStep.CREATE_ADS:
                adv_assets = self.getDb().adv_assets(self.userMarketplace.uid, ObjectId(self.userMarketplace.id))
                for assetType in [AdAssetType.AD_GROUP, AdAssetType.CAMPAIGN, AdAssetType.PORTFOLIO, AdAssetType.AD]:
                    pipeline = [ { '$match': { 'uid': self.userMarketplace.uid, 'marketplace': ObjectId(self.userMarketplace.id), 'assettype': 'Ad' } }, { '$lookup': { 'from': 'adv_assets', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'assettype': 'Campaign', 'id': '$campaignid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$id', '$$id' ] } ] } } }, { '$project': { 'portfolioid': 1, '_id': 0 } } ], 'as': 'portfolioid' } }, { '$replaceWith': { 'uid': '$uid', 'marketplace': '$marketplace', 'products': '$creative.products', 'campaignid': '$campaignid', 'adgroupid': '$adgroupid', 'portfolioid': { '$getField': { 'input': { '$first': '$portfolioid' }, 'field': 'portfolioid' } }, 'adid': '$id' } }, { '$unwind': '$products' }, { '$match': { 'products.productIdType': 'ASIN' } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'campaignid': '$campaignid', 'adgroupid': '$adgroupid', 'portfolioid': '$portfolioid', 'adid': '$adid', 'product': '$products.productId' } } }, { '$replaceWith': '$_id' }, { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$product' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$set': { 'image': { '$first': '$images' } } }, { '$project': { 'sku': 1, 'asin': 1, 'image': 1, '_id': 0 } } ], 'as': 'product' } }, { '$unwind': { 'path': '$product' } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'id': '$adid' if assetType==AdAssetType.AD else '$adgroupid' if assetType==AdAssetType.AD_GROUP else '$campaignid' if assetType==AdAssetType.CAMPAIGN else '$portfolioid', }, 'products': { '$push': '$product' }, 'count': { '$sum': 1 } } }, { '$set': { 'products': { '$slice': [ '$products', 10 ] } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'products': '$products' }, { '$cond': [ { '$gt': [ '$count', 10 ] }, { 'count': { '$subtract': [ '$count', 10 ] } }, {} ] } ] } } }, { '$set': { '_id': { '$concat': [ { '$toString': '$marketplace' }, '_', '$id' ] } } }, { '$project': { 'products': 1, 'count': 1 } }, { '$merge': { 'into': 'adv_ads' } } ]
                    await adv_assets.db.aggregate(pipeline)
                return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
            elif self.message.step==AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS:
                from amazon_daily_report.reports.pipelines.StateAndDateAnalytics import AnalyticsProcessor
                processor = AnalyticsProcessor(self.userMarketplace,self.report, self.getDb())
                if self.message.date: 
                    self.message.date = await processor.executeDate(self.message.date)
                    if self.message.date:return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
                    else:return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_QUERIES)
                else:
                    self.message.date = await processor.addDateToOrderItems()
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
            elif self.message.step==AmazonDailyReportAggregationStep.ADD_QUERIES:
                from amazon_daily_report.reports.pipelines.ProductQueryBuilder import QueryBuilder
                builder = QueryBuilder(self.userMarketplace, self.report, self.getDb())
                if self.message.query:
                    print(self.message.query.tag.value)
                    self.message.query = await builder.execute(self.message.query)
                    print(self.message.query.tag.value) if self.message.query else print(None)
                    if self.message.query is not None: return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_QUERIES)
                    else: return await self.__sendMessage(AmazonDailyReportAggregationStep.MARK_COMPLETION)
                else:
                    self.message.query = await builder.getNextQuery(None)
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_QUERIES)
            elif self.message.step==AmazonDailyReportAggregationStep.MARK_COMPLETION:
                await self.reportsDb.deleteChildReports(self.message.index)
                await self.reportsDb.markParentAsCompleted(self.message.index)
                if self.report.createdat:
                    await self.getDb().marketplaces(self.userMarketplace.uid).completeReportProcessing(
                            self.userMarketplace.id, self.report.startdate, self.report.enddate, self.report.createdat, reportid
                        )
                return None

    async def __sendMessage(self, step: AmazonDailyReportAggregationStep, delay: int=0):
        await self.sqsDb.setMessageAsCompleted(self.messageId)
        self.message.step = step
        messageId = (await self.sqs.mockMessage(SendMessageRequest(QueueUrl=QueueUrl.AMAZON_REPORTS, DelaySeconds=delay), self.message)).message_id
        return self.message, messageId

    def getDb(self) -> DbClient:
        if self.db is None:
            MONGOURI = self.secrets.MONGO_DB_CONNECT_URI
            self.db = DbClient(MONGOURI)
        return self.db
    
    async def getSpapiClient(self) -> SpApiClient:
        if self.spapi is None:
            # obj = AmazonApiObject(** await self.getDb().marketplaces(self.uid).getMarketplaceApiObject(self.marketplace, AmazonAccountType.SPAPI))
            self.spapi = AmazonApiClient(self.userMarketplace.spapi).spapi
        return self.spapi
    
    async def getAdApiClient(self) -> AdApiClient:
        if self.adApi is None:
            # obj = AmazonApiObject(** await self.getDb().marketplaces(self.uid).getMarketplaceApiObject(self.marketplace, AmazonAccountType.ADVERTISING))
            self.adApi = AmazonApiClient(self.userMarketplace.ad).ad
        return self.adApi

    async def getSPAPIReportManager(self) -> AmazonSpapiReportManager:
        if self.spapiReportManager is None:
            spapi = await self.getSpapiClient()
            self.spapiReportManager = AmazonSpapiReportManager(self.userMarketplace, spapi)
        return self.spapiReportManager

    async def getDataKioskReportManager(self) -> AmazonDataKioskReportManager:
        if self.dataKioskReportManager is None:
            spapi = await self.getSpapiClient()
            self.dataKioskReportManager = AmazonDataKioskReportManager(self.userMarketplace, spapi)
        return self.dataKioskReportManager

    async def getAdReportManager(self) -> AmazonAdsReportManager:
        if self.adReportManager is None:
            adapi = await self.getAdApiClient()
            self.adReportManager = AmazonAdsReportManager(self.userMarketplace, adapi)
        return self.adReportManager
    
    async def getAdExportManager(self) -> AmazonAdsExportManager:
        if self.adExportManager is None:
            adapi = await self.getAdApiClient()
            self.adExportManager = AmazonAdsExportManager(self.userMarketplace, adapi)
        return self.adExportManager

    def getAmazonDailyReportDbHelper(self)->AmazonDailyReportHelper:
        if self.reportsDb is None:
            self.reportsDb = self.getDb().amazon_daily_reports(self.userMarketplace.uid, ObjectId(self.userMarketplace.id))
        return self.reportsDb
    
    

    async def createReports(self):
        months = 2 if not self.userMarketplace.startdate else 1
        from amazon_daily_report.reports import Utility
        endDate = Utility.getEndDate(self.userMarketplace.details.timezone)
        startDate = self.helper.modify(False, endDate, months=months)
        spapiReports = await (await self.getSPAPIReportManager()).getSPAPIReportsConf(startDate, months)
        adReports = (await self.getAdReportManager()).getReportsConf(months)
        adExports = await (await self.getAdExportManager()).createExports()
        kioskReports = (await self.getDataKioskReportManager()).getDataKioskReportsConf(months)
        # reports: list[dict] = []
        reports: dict[AmazonReportType, list[AmazonSpapiReport]|list[AmazonAdReport]|list[AmazonExportReport]|list[AmazonDataKioskReport]] = {
            AmazonReportType.SPAPI: spapiReports,
            AmazonReportType.AD: adReports,
            AmazonReportType.AD_EXPORT: adExports,
            AmazonReportType.KIOSK: kioskReports
        }
        self.message.index = str(await self.getAmazonDailyReportDbHelper().insertParentReport(startDate, endDate, reports))
        await self.sqsDb.addIndex(self.messageId,self.message.index)
        return await self.__sendMessage(AmazonDailyReportAggregationStep.PROCESS_REPORTS)
        # self.marketplace.startDate = SellerManager(self.user).updateMarketplaceStartDate(self.marketplace.id, startDate)

    async def processReports(self):
        shouldContinue = any(x.error is not None for x in self.report.spapi+self.report.ad+self.report.adexport+self.report.kiosk)
        reportUtil = ReportUtil(self.userMarketplace)
        while shouldContinue:
            isListingFileProcessed = await (await self.getSPAPIReportManager()).processSpapiReports(self.report.spapi, reportUtil, self.getDb(), self.report.id)
            if isListingFileProcessed: await self.startProductsParallel()
            await (await self.getDataKioskReportManager()).processDataKioskReports(self.report.kiosk, reportUtil, self.getDb(), self.report.id)
            await (await self.getAdExportManager()).processExportReports(self.report.adexport, reportUtil, self.getDb(), self.report.id)
            await (await self.getAdReportManager()).processAdReports(self.report.ad, reportUtil, self.getDb(), self.report.id)

    async def startProductsParallel(self):
        if not self.message.date: self.message.date = self.userMarketplace.lastrefresh
        return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PRODUCTS)








    




    