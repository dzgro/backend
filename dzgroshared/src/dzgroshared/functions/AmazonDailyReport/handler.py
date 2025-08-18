from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import LambdaContext
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.functions.AmazonDailyReport.reports.ReportUtils import ReportUtil
from dzgroshared.functions.AmazonDailyReport.reports.report_types.adexport.AdsExportApp import AmazonAdsExportManager
from dzgroshared.functions.AmazonDailyReport.reports.report_types.datakiosk.DataKioskReportApp import AmazonDataKioskReportManager
from dzgroshared.amazonapi import AmazonApiObject
from bson import ObjectId
from dzgroshared.db.collections.products import ProductHelper
from dzgroshared.db.collections.queue_messages import QueueMessagesHelper
from dzgroshared.models.collections.queue_messages import AmazonParentReportQueueMessage
from dzgroshared.models.enums import AdAssetType, AmazonAccountType, AmazonDailyReportAggregationStep, AmazonReportType, CollectionType, QueueUrl, SQSMessageStatus
from dzgroshared.models.extras.amazon_daily_report import AmazonAdReport, AmazonDataKioskReport, AmazonExportReport, AmazonParentReport, MarketplaceObjectForReport, AmazonSpapiReport
from dzgroshared.utils.date_util import DateHelper
from dzgroshared.functions.AmazonDailyReport.reports.report_types.spapi.SpapiReportApp import AmazonSpapiReportManager
from dzgroshared.functions.AmazonDailyReport.reports.report_types.adexport.AdsExportApp import AmazonAdsExportManager
from dzgroshared.functions.AmazonDailyReport.reports.report_types.datakiosk.DataKioskReportApp import AmazonDataKioskReportManager
from dzgroshared.functions.AmazonDailyReport.reports.report_types.ad.AdsReportApp import AmazonAdsReportManager
from dzgroshared.models.sqs import SendMessageRequest

class AmazonReportManager:
    client: DzgroSharedClient
    event: dict
    context: LambdaContext
    userMarketplace: MarketplaceObjectForReport
    sqsDb: QueueMessagesHelper
    productsDb: ProductHelper
    spapiReportManager: AmazonSpapiReportManager
    dataKioskReportManager: AmazonDataKioskReportManager
    adReportManager: AmazonAdsReportManager
    adExportManager: AmazonAdsExportManager
    helper: DateHelper
    report: AmazonParentReport
    messageId: str
    reportUti: ReportUtil

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event: dict, context: LambdaContext):
        self.event = event
        self.context = context
        parsed = SQSEvent.model_validate(self.event)
        for record in parsed.Records:
            message = AmazonParentReportQueueMessage.model_validate(record.dictBody)
            self.client.setUid(message.uid)
            self.client.setMarketplace(message.marketplace)
            self.messageId = record.messageId
            self.message = message

    def __getattr__(self, item):
        return None
    
    async def checkMessage(self):
        try:
            dbMessageStatus = await self.sqsDb.getMessageStatus(self.messageId)
            if dbMessageStatus==SQSMessageStatus.PENDING: 
                # await self.sqsDb.setMessageAsProcessing(self.messageId)
                await self.setUserMarketplace()
                return await self.executeMessage()
            return None
        except Exception as e:
            error = e.args[0] if len(e.args)>0 else "Some error Occurred"
            await self.sqsDb.setMessageAsFailed(self.messageId, error)
            if self.report: await self.client.db.amazon_daily_reports.terminateParent(self.report.id, error)
    
    async def setUserMarketplace(self):
        self.userMarketplace = MarketplaceObjectForReport(**await self.client.db.marketplaces.getMarketplaceObjectForReport(ObjectId(self.message.marketplace)))
        self.reportUtil = ReportUtil(self.client, self.userMarketplace)

    async def executeMessage(self)->tuple[AmazonParentReportQueueMessage, str]|None:
        if not self.message.index:
            if self.message.step==AmazonDailyReportAggregationStep.CREATE_REPORTS:
                return await self.createReports()
        else:
            reportid = ObjectId(self.message.index)
            self.report = await self.client.db.amazon_daily_reports.getParentReport(reportid)
            if self.message.step==AmazonDailyReportAggregationStep.ADD_PRODUCTS:
                from dzgroshared.functions.AmazonDailyReport.reports.AddProducts import ListingsBuilder
                builder = ListingsBuilder(self.client,self.context, self.userMarketplace, await self.spapi(), self.reportUtil, self.report.id)
                self.message.date = await builder.execute(self.message.date)
                if self.message.date: return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PRODUCTS)
                else:
                    await self.client.db.amazon_daily_reports.markProductsComplete(reportid)
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS)
            elif self.message.step==AmazonDailyReportAggregationStep.PROCESS_REPORTS: 
                if self.report.progress!=100: 
                    await self.processReports()
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.PROCESS_REPORTS, delay=10)
                else:
                    await self.client.db.amazon_daily_reports.markReportsComplete(reportid)
                    # if self.report.productsComplete: return self.sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS)
                    # return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS)
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PRODUCTS)
            elif self.message.step==AmazonDailyReportAggregationStep.ADD_PORTFOLIOS:
                if not self.report.productsComplete or self.report.progress!=100:
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS, delay=60)
                else:
                    from dzgroshared.functions.AmazonDailyReport.reports.pipelines.AddPortfolios import PortfolioProcessor
                    portfolios = await PortfolioProcessor(self.userMarketplace, await self.adapi()).getPortfolios()
                    await self.reportUtil.update(self.client.db, CollectionType.ADV_ASSETS, portfolios, self.report.id)
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_ADS)
            elif self.message.step==AmazonDailyReportAggregationStep.CREATE_ADS:
                for assetType in [AdAssetType.AD_GROUP, AdAssetType.CAMPAIGN, AdAssetType.PORTFOLIO, AdAssetType.AD]:
                    pipeline = [ { '$match': { 'uid': self.userMarketplace.uid, 'marketplace': ObjectId(self.userMarketplace.id), 'assettype': 'Ad' } }, { '$lookup': { 'from': 'adv_assets', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'assettype': 'Campaign', 'id': '$campaignid' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$assettype', '$$assettype' ] }, { '$eq': [ '$id', '$$id' ] } ] } } }, { '$project': { 'portfolioid': 1, '_id': 0 } } ], 'as': 'portfolioid' } }, { '$replaceWith': { 'uid': '$uid', 'marketplace': '$marketplace', 'products': '$creative.products', 'campaignid': '$campaignid', 'adgroupid': '$adgroupid', 'portfolioid': { '$getField': { 'input': { '$first': '$portfolioid' }, 'field': 'portfolioid' } }, 'adid': '$id' } }, { '$unwind': '$products' }, { '$match': { 'products.productIdType': 'ASIN' } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'campaignid': '$campaignid', 'adgroupid': '$adgroupid', 'portfolioid': '$portfolioid', 'adid': '$adid', 'product': '$products.productId' } } }, { '$replaceWith': '$_id' }, { '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'asin': '$product' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$asin', '$$asin' ] } ] } } }, { '$set': { 'image': { '$first': '$images' } } }, { '$project': { 'sku': 1, 'asin': 1, 'image': 1, '_id': 0 } } ], 'as': 'product' } }, { '$unwind': { 'path': '$product' } }, { '$group': { '_id': { 'uid': '$uid', 'marketplace': '$marketplace', 'id': '$adid' if assetType==AdAssetType.AD else '$adgroupid' if assetType==AdAssetType.AD_GROUP else '$campaignid' if assetType==AdAssetType.CAMPAIGN else '$portfolioid', }, 'products': { '$push': '$product' }, 'count': { '$sum': 1 } } }, { '$set': { 'products': { '$slice': [ '$products', 10 ] } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'products': '$products' }, { '$cond': [ { '$gt': [ '$count', 10 ] }, { 'count': { '$subtract': [ '$count', 10 ] } }, {} ] } ] } } }, { '$set': { '_id': { '$concat': [ { '$toString': '$marketplace' }, '_', '$id' ] } } }, { '$project': { 'products': 1, 'count': 1 } }, { '$merge': { 'into': 'adv_ads' } } ]
                    await self.client.db.adv_assets.db.aggregate(pipeline)
                return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
            elif self.message.step==AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS:
                from dzgroshared.functions.AmazonDailyReport.reports.pipelines.StateAndDateAnalytics import AnalyticsProcessor
                processor = AnalyticsProcessor(self.client.db, self.userMarketplace,self.report)
                if self.message.date: 
                    self.message.date = await processor.executeDate(self.message.date)
                    if self.message.date:return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
                    else:return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_QUERIES)
                else:
                    self.message.date = await processor.addDateToOrderItems()
                    return await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
            elif self.message.step==AmazonDailyReportAggregationStep.ADD_QUERIES:
                from dzgroshared.functions.AmazonDailyReport.reports.pipelines.ProductQueryBuilder import QueryBuilder
                builder = QueryBuilder(self.client.db, self.userMarketplace, self.report)
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
                await self.client.db.amazon_daily_reports.deleteChildReports(self.message.index)
                await self.client.db.amazon_daily_reports.markParentAsCompleted(self.message.index)
                if self.report.createdat:
                    await self.client.db.marketplaces.completeReportProcessing(
                            self.userMarketplace.id, self.report.dates[0], self.report.dates[-1], self.report.createdat, reportid
                        )
                return None

    async def __sendMessage(self, step: AmazonDailyReportAggregationStep, delay: int=0):
        await self.sqsDb.setMessageAsCompleted(self.messageId)
        self.message.step = step
        messageId = (await self.client.sqs.mockMessage(SendMessageRequest(QueueUrl=QueueUrl.AMAZON_REPORTS, DelaySeconds=delay), self.message)).message_id
        return self.message, messageId

    async def spapi(self):
        if self.spapiClient is None:
            obj = AmazonApiObject(**await self.client.db.marketplaces.getMarketplaceApiObject(
                self.userMarketplace.id,self.client.secrets.SPAPI_CLIENT_ID,
                self.client.secrets.SPAPI_CLIENT_SECRET, AmazonAccountType.SPAPI))
            self.spapiClient = self.client.amazonapi(obj).spapi
        return self.spapiClient

    async def adapi(self):
        if self.adapiClient is None:
            obj = AmazonApiObject(**await self.client.db.marketplaces.getMarketplaceApiObject(
                self.userMarketplace.id,self.client.secrets.ADS_CLIENT_ID,
                self.client.secrets.ADS_CLIENT_SECRET, AmazonAccountType.ADVERTISING))
            self.adapiClient = self.client.amazonapi(obj).ad
        return self.adapiClient

    async def getSPAPIReportManager(self) -> AmazonSpapiReportManager:
        if self.spapiReportManager is None:
            self.spapiReportManager = AmazonSpapiReportManager(self.client, self.userMarketplace, await self.spapi())
        return self.spapiReportManager

    async def getDataKioskReportManager(self) -> AmazonDataKioskReportManager:
        if self.dataKioskReportManager is None:
            self.dataKioskReportManager = AmazonDataKioskReportManager(self.client, self.userMarketplace, await self.spapi())
        return self.dataKioskReportManager

    async def getAdReportManager(self) -> AmazonAdsReportManager:
        if self.adReportManager is None:
            self.adReportManager = AmazonAdsReportManager(self.client, self.userMarketplace, await self.adapi())
        return self.adReportManager
    
    async def getAdExportManager(self) -> AmazonAdsExportManager:
        if self.adExportManager is None:
            self.adExportManager = AmazonAdsExportManager(self.client, self.userMarketplace, await self.adapi())
        return self.adExportManager
    
    async def createReports(self):
        months = 2 if not self.userMarketplace.startdate else 1
        from dzgroshared.functions.AmazonDailyReport.reports import Utility
        endDate = Utility.getEndDate(self.userMarketplace.details.timezone)
        startDate = self.helper.modify(False, endDate, months=months)
        spapiReports = await (await self.getSPAPIReportManager()).getSPAPIReportsConf(startDate, months)
        adReports = (await self.getAdReportManager()).getReportsConf(months)
        adExports = await (await self.getAdExportManager()).createExports()
        kioskReports = (await self.getDataKioskReportManager()).getDataKioskReportsConf(months)
        # reports: list[dict] = []
        reports: dict[AmazonReportType, list[AmazonSpapiReport]|list[AmazonAdReport]|list[AmazonExportReport]|list[AmazonDataKioskReport]] = {
            # AmazonReportType.SPAPI: spapiReports,
            AmazonReportType.AD: adReports,
            # AmazonReportType.AD_EXPORT: adExports,
            # AmazonReportType.KIOSK: kioskReports
        }
        self.message.index = str(await self.client.db.amazon_daily_reports.insertParentReport(startDate, endDate, reports))
        await self.sqsDb.addIndex(self.messageId,self.message.index)
        return await self.__sendMessage(AmazonDailyReportAggregationStep.PROCESS_REPORTS)
        # self.marketplace.startDate = SellerManager(self.user).updateMarketplaceStartDate(self.marketplace.id, startDate)

    async def processReports(self):
        shouldContinue = any(x.error is None for x in self.report.spapi+self.report.ad+self.report.adexport+self.report.kiosk)
        if shouldContinue:
            print("Progress: ", self.report.progress)
            isListingFileProcessed = await (await self.getSPAPIReportManager()).processSpapiReports(self.report.spapi, self.reportUtil, self.report.id)
            # if isListingFileProcessed: await self.startProductsParallel()
            await (await self.getDataKioskReportManager()).processDataKioskReports(self.report.kiosk, self.reportUtil, self.report.id)
            await (await self.getAdExportManager()).processExportReports(self.report.adexport, self.reportUtil, self.report.id)
            await (await self.getAdReportManager()).processAdReports(self.report.ad, self.reportUtil, self.report.id)

    async def startProductsParallel(self):
        if not self.message.date: self.message.date = self.userMarketplace.lastrefresh
        return await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PRODUCTS)








    




    