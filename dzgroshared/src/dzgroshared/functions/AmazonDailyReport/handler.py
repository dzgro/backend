
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import LambdaContext
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.functions.AmazonDailyReport.reports.ReportUtils import ReportUtil
from dzgroshared.functions.AmazonDailyReport.reports.report_types.adexport.AdsExportApp import AmazonAdsExportManager
from dzgroshared.functions.AmazonDailyReport.reports.report_types.datakiosk.DataKioskReportApp import AmazonDataKioskReportManager
from bson import ObjectId
from dzgroshared.db.collections.products import ProductHelper
from dzgroshared.models.collections.queue_messages import AmazonParentReportQueueMessage
from dzgroshared.models.enums import AdAssetType, AmazonAccountType, AmazonDailyReportAggregationStep, AmazonReportType, CollectionType, QueueName, SQSMessageStatus, ENVIRONMENT
from dzgroshared.models.extras.amazon_daily_report import AmazonAdReport, AmazonDataKioskReport, AmazonExportReport, AmazonParentReport, MarketplaceObjectForReport, AmazonSpapiReport
from dzgroshared.utils import date_util
from dzgroshared.models.sqs import SendMessageRequest

class AmazonReportManager:
    client: DzgroSharedClient
    event: SQSEvent
    context: LambdaContext
    userMarketplace: MarketplaceObjectForReport
    productsDb: ProductHelper
    report: AmazonParentReport
    messageId: str
    reportUti: ReportUtil

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event: dict|SQSEvent, context: LambdaContext):
        try:
            self.event = SQSEvent.model_validate(self.event) if isinstance(event, dict) else event
            self.context = context
            for record in self.event.Records:
                try:
                    message = AmazonParentReportQueueMessage.model_validate(record.dictBody)
                    self.client.setUid(message.uid)
                    self.client.setMarketplace(message.marketplace)
                    self.messageId = record.messageId
                    self.message = message
                    return await self.checkMessage()
                except Exception as e:
                    error = e.args[0] if len(e.args) > 0 else "Some error Occurred"
                    if self.message.index:
                        await self.client.db.amazon_daily_reports.terminateParent(self.message.index, error)
                    raise e
        except Exception as e:
            error = e.args[0] if len(e.args) > 0 else "Some error Occurred"
            await self.client.db.sqs_messages.setMessageAsFailed(self.messageId, error)
            print(f"Error in AmazonReportManager: {error}")

    def __getattr__(self, item):
        return None
    
    async def checkMessage(self):
        dbMessageStatus = await self.client.db.sqs_messages.getMessageStatus(self.messageId)
        if dbMessageStatus==SQSMessageStatus.PENDING: 
            # await self.client.db.sqs_messages.setMessageAsProcessing(self.messageId)
            await self.setUserMarketplace()
            delay = await self.executeMessage()
            return await self.exitAndContinue(delay)
    
    async def setUserMarketplace(self):
        self.userMarketplace = MarketplaceObjectForReport(**await self.client.db.marketplaces.getMarketplaceObjectForReport(ObjectId(self.message.marketplace)))
        self.userMarketplace.spapi.client_id = self.client.secrets.SPAPI_CLIENT_ID
        self.userMarketplace.spapi.client_secret = self.client.secrets.SPAPI_CLIENT_SECRET
        self.userMarketplace.ad.client_id = self.client.secrets.ADS_CLIENT_ID
        self.userMarketplace.ad.client_secret = self.client.secrets.ADS_CLIENT_SECRET
        self.reportUtil = ReportUtil(self.client)

    async def executeMessage(self)->int:
        if not self.message.index:
            if self.message.step==AmazonDailyReportAggregationStep.CREATE_REPORTS: await self.createReports()
        else:
            reportid = ObjectId(self.message.index)
            self.report = await self.client.db.amazon_daily_reports.getParentReport(reportid)
            if self.message.step==AmazonDailyReportAggregationStep.ADD_PRODUCTS:
                from dzgroshared.functions.AmazonDailyReport.reports.AddProducts import ListingsBuilder
                builder = ListingsBuilder(self.client,self.context, self.userMarketplace, self.spapi, self.reportUtil, self.report.id)
                self.message.date = await builder.execute(self.message.date)
                if not self.message.date: await self.client.db.amazon_daily_reports.markProductsComplete(reportid)
            elif self.message.step==AmazonDailyReportAggregationStep.PROCESS_REPORTS: 
                if self.report.progress!=100: await self.processReports()
                return 10 if self.report.progress!=100 else 0
            elif self.message.step==AmazonDailyReportAggregationStep.ADD_PORTFOLIOS:
                from dzgroshared.functions.AmazonDailyReport.reports.pipelines.AddPortfolios import PortfolioProcessor
                portfolios = await PortfolioProcessor(self.userMarketplace, self.adapi).getPortfolios()
                await self.reportUtil.update(CollectionType.ADV_ASSETS, portfolios, self.report.id)
            elif self.message.step==AmazonDailyReportAggregationStep.CREATE_ADS:
                await self.client.db.adv_ads.refreshAll()
                await self.client.db.state_analytics.db.deleteMany({"date": {"$gt": self.report.dates[0]}})
                await self.client.db.date_analytics.db.deleteMany({"date": {"$gt": self.report.dates[0]}})
            elif self.message.step==AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS:
                from dzgroshared.functions.AmazonDailyReport.reports.pipelines.StateAndDateAnalytics import AnalyticsProcessor
                self.message.date = await AnalyticsProcessor(self.client.db,self.report.dates).executeDate(self.message.date or self.report.dates[-1])
                if not self.message.date: await self.client.db.query_results.db.deleteMany({})
            elif self.message.step==AmazonDailyReportAggregationStep.ADD_QUERIES:
                from dzgroshared.functions.AmazonDailyReport.reports.pipelines.ProductQueryBuilder import QueryBuilder
                builder = QueryBuilder(self.client.db, self.report.startdate, self.report.enddate)
                if not self.message.query: self.message.query = await builder.getNextQuery(None)
                else: self.message.query = await builder.execute(self.message.query)
            elif self.message.step==AmazonDailyReportAggregationStep.MARK_COMPLETION:
                await self.client.db.amazon_daily_reports.deleteChildReports(self.message.index)
                await self.client.db.amazon_daily_reports.markParentAsCompleted(self.message.index)
                if self.report.createdat:
                    await self.client.db.marketplaces.completeReportProcessing(
                            self.userMarketplace.id, self.report.dates[0], self.report.dates[-1], self.report.createdat, reportid
                        )
        return 0

    async def __sendMessage(self, step: AmazonDailyReportAggregationStep, delay: int=0):
        await self.client.db.sqs_messages.setMessageAsCompleted(self.messageId)
        self.message.step = step
        queue = QueueName.AMAZON_REPORTS if self.client.env != ENVIRONMENT.DEV else QueueName.AMAZON_REPORTS_TEST
        return await self.client.sqs.sendMessage(SendMessageRequest(QueueUrl=queue, DelaySeconds=delay), self.message, {'ram': self.context.memory_limit_in_mb, 'funcname': self.context.function_name})

    @property
    def spapi(self):
        return self.client.spapi(self.userMarketplace.spapi)

    @property
    def adapi(self):
        return self.client.adapi(self.userMarketplace.ad)

    async def getSPAPIReportManager(self):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.spapi.SpapiReportApp import AmazonSpapiReportManager
        return AmazonSpapiReportManager(self.client, self.userMarketplace, self.spapi)
        
    async def getDataKioskReportManager(self):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.datakiosk.DataKioskReportApp import AmazonDataKioskReportManager
        return AmazonDataKioskReportManager(self.client, self.userMarketplace, self.spapi)

    async def getAdReportManager(self):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.ad.AdsReportApp import AmazonAdsReportManager
        return AmazonAdsReportManager(self.client, self.userMarketplace, self.adapi)

    async def getAdExportManager(self):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.adexport.AdsExportApp import AmazonAdsExportManager
        return AmazonAdsExportManager(self.client, self.userMarketplace, self.adapi)
    
    async def createReports(self):
        months = 2 if not self.userMarketplace.startdate else 1
        from dzgroshared.functions.AmazonDailyReport.reports import Utility
        endDate = Utility.getEndDate(self.userMarketplace.details.timezone)
        startDate = date_util.subtract(endDate, months=months)
        spapiReports = await (await self.getSPAPIReportManager()).getSPAPIReportsConf(startDate, months)
        adReports = (await self.getAdReportManager()).getReportsConf(months)
        adExports = await (await self.getAdExportManager()).createExports()
        kioskReports = (await self.getDataKioskReportManager()).getDataKioskReportsConf(months)
        reports: dict[AmazonReportType, list[AmazonSpapiReport]|list[AmazonAdReport]|list[AmazonExportReport]|list[AmazonDataKioskReport]] = {
            # AmazonReportType.SPAPI: spapiReports,
            # AmazonReportType.AD: adReports,
            AmazonReportType.AD_EXPORT: adExports,
            # AmazonReportType.KIOSK: kioskReports
        }
        self.message.index = str(await self.client.db.amazon_daily_reports.insertParentReport(startDate, endDate, reports))
        await self.client.db.sqs_messages.addIndex(self.messageId,self.message.index)
        
    async def processReports(self):
        shouldContinue = any(x.error is None for x in self.report.spapi+self.report.ad+self.report.adexport+self.report.kiosk)
        if shouldContinue:
            print("Progress: ", self.report.progress)
            await (await self.getSPAPIReportManager()).processSpapiReports(self.report.spapi, self.reportUtil, self.report.id)
            await (await self.getDataKioskReportManager()).processDataKioskReports(self.report.kiosk, self.reportUtil, self.report.id)
            await (await self.getAdExportManager()).processExportReports(self.report.adexport, self.reportUtil, self.report.id)
            await (await self.getAdReportManager()).processAdReports(self.report.ad, self.reportUtil, self.report.id)

        spapiReportTypes = set(list(map(lambda x: x.req.report_type if x.req else None, self.report.spapi)))
        for report in spapiReportTypes:
            if report:
                reports = list(filter(lambda x: x.req.report_type == report if x.req else False, self.report.spapi))
                created = len(list(filter(lambda x: x.res is not None, reports)))
                saved = len(list(filter(lambda x: x.filepath is not None, reports)))
                if created>0 and saved!=created:
                    print(f"SPAPI {report.value} Total: {len(reports)}, Created: {created}, Saved: {saved}")
        adReportTypes = set(list(map(lambda x: x.req.configuration.reportTypeId if x.req else None, self.report.ad)))
        for report in adReportTypes:
            if report:
                reports = list(filter(lambda x: x.req.configuration.reportTypeId == report if x.req else False, self.report.ad))
                created = len(list(filter(lambda x: x.res is not None, reports)))
                saved = len(list(filter(lambda x: x.filepath is not None, reports)))
                if created>0 and saved!=created:
                    print(f"Ad {report.value} Total: {len(reports)}, Created: {created}, Saved: {saved}")
        created = len(list(filter(lambda x: x.res is not None, self.report.kiosk)))
        saved = len(list(filter(lambda x: x.filepath is not None, self.report.kiosk)))
        if created>0 and saved!=created:
            print(f"Kiosk Total: {len(self.report.kiosk)}, Created: {created}, Saved: {saved}")
        
        created = len(list(filter(lambda x: x.res is not None, self.report.adexport)))
        saved = len(list(filter(lambda x: x.filepath is not None, self.report.adexport)))
        if created>0 and saved!=created:
            print(f"AdExport Total: {len(self.report.adexport)}, Created: {created}, Saved: {saved}")
        

    
    async def exitAndContinue(self, delay: int=0):
        if self.message.step==AmazonDailyReportAggregationStep.CREATE_REPORTS:
            await self.__sendMessage(AmazonDailyReportAggregationStep.PROCESS_REPORTS)
            if self.client.env==ENVIRONMENT.DEV:self.userMarketplace.lastrefresh = date_util.getCurrentDateTime()
            if not self.message.date: self.message.date = self.userMarketplace.lastrefresh
            await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PRODUCTS)
        elif self.message.step==AmazonDailyReportAggregationStep.ADD_PRODUCTS:
            if self.message.date: await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PRODUCTS)
            else: return None
        elif self.message.step==AmazonDailyReportAggregationStep.PROCESS_REPORTS:
            if delay==0:
                if self.report.productsComplete: await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_PORTFOLIOS, delay=delay)
                else: await self.__sendMessage(AmazonDailyReportAggregationStep.PROCESS_REPORTS, delay=60)
            else: 
                await self.__sendMessage(AmazonDailyReportAggregationStep.PROCESS_REPORTS, delay=delay)
        elif self.message.step==AmazonDailyReportAggregationStep.ADD_PORTFOLIOS:
            await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_ADS)
        elif self.message.step==AmazonDailyReportAggregationStep.CREATE_ADS:
            await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
        elif self.message.step==AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS:
            if self.message.date: await self.__sendMessage(AmazonDailyReportAggregationStep.CREATE_STATE_DATE_ANALYTICS)
            else: await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_QUERIES)
        elif self.message.step==AmazonDailyReportAggregationStep.ADD_QUERIES:
            if self.message.query: await self.__sendMessage(AmazonDailyReportAggregationStep.ADD_QUERIES)
            else: await self.__sendMessage(AmazonDailyReportAggregationStep.MARK_COMPLETION)
        else: return None
        return delay






    




    