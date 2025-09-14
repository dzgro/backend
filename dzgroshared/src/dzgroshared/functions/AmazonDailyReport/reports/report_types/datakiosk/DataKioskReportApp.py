import json
from dzgroshared.db.model import DzgroError
from dzgroshared.amazonapi.spapi import SpApiClient
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.amazonapi.spapi.datakiosk import DataKioskCreateQueryRequest, DataKioskQueryResponse, DataKioskDocumentResponse, DataKioskCreateQuerySpecification
from dzgroshared.models.amazonapi.spapi.reports import ProcessingStatus
from dzgroshared.db.enums import CollectionType, DataKioskType
from dzgroshared.db.daily_report_group.model import AmazonDataKioskReport, AmazonDataKioskReportDB, MarketplaceObjectForReport
from dzgroshared.functions.AmazonDailyReport.reports import DateUtility
from dzgroshared.functions.AmazonDailyReport.reports.ReportUtils import ReportUtil
from dzgroshared.db.model import ErrorDetail, ErrorList, PyObjectId
from dzgroshared.functions.AmazonDailyReport.reports.DateUtility import MarketplaceDatesUtility

class AmazonDataKioskReportManager:
    client: DzgroSharedClient
    spapi: SpApiClient
    timezone: str
    createThrottle: bool = False
    getThrottle: bool = False
    getDocumentThrottle: bool = False
    marketplace: MarketplaceObjectForReport
    reportUtil: ReportUtil
    reportId: PyObjectId
    dateUtil: MarketplaceDatesUtility


    def __init__(self, client: DzgroSharedClient, marketplace: MarketplaceObjectForReport, spapi: SpApiClient, dateUtil: MarketplaceDatesUtility) -> None:
        self.client = client
        self.spapi = spapi
        self.timezone = marketplace.details.timezone
        self.marketplace = marketplace
        self.dateUtil = dateUtil

    def getDataKioskReportsConf(self)->list[AmazonDataKioskReport]:
        reports: list[AmazonDataKioskReport] = []
        reports.extend(self.__getAsinTrafficReportsConf())
        # reports.extend(self.__getSkuEconomicsConf())
        return reports 

    def __getAsinTrafficReportsConf(self)->list[AmazonDataKioskReport]:
        dates = self.dateUtil.getTrafficKioskReportDates()
        reports: list[AmazonDataKioskReport] = []
        for date in dates:
            query = 'query MyQuery{analytics_salesAndTraffic_2024_04_24{salesAndTrafficByAsin(aggregateBy:PARENT endDate:"'+date+'" marketplaceIds:["'+self.spapi.object.marketplaceid+'"] startDate:"'+date+'"){childAsin endDate marketplaceId parentAsin sales{orderedProductSales{amount currencyCode}orderedProductSalesB2B{amount currencyCode}totalOrderItems totalOrderItemsB2B unitsOrdered unitsOrderedB2B}sku startDate traffic{browserPageViews browserPageViewsB2B browserPageViewsPercentage browserPageViewsPercentageB2B browserSessionPercentage browserSessions browserSessionPercentageB2B browserSessionsB2B buyBoxPercentage buyBoxPercentageB2B mobileAppPageViews mobileAppPageViewsPercentage mobileAppPageViewsB2B mobileAppPageViewsPercentageB2B mobileAppSessionPercentageB2B mobileAppSessionPercentage mobileAppSessions mobileAppSessionsB2B pageViews pageViewsB2B pageViewsPercentage pageViewsPercentageB2B sessionPercentage sessionPercentageB2B sessions sessionsB2B unitSessionPercentage unitSessionPercentageB2B}}}}'
            reports.append(AmazonDataKioskReport(reporttype=DataKioskType.SALES_TRAFFIC_ASIN, req=DataKioskCreateQueryRequest(body=DataKioskCreateQuerySpecification(query=query))))
        return reports

    def __getSkuEconomicsConf(self)->list[AmazonDataKioskReport]:
        isNew = self.marketplace.dates is None
        dates = self.dateUtil.getEconomicsKioskReportDates()
        reports: list[AmazonDataKioskReport] = []
        for date in dates:
            startDate, endDate = date
            query = 'query MyQuery{analytics_economics_2024_03_15{economics(endDate:"'+endDate+'" marketplaceIds:"" startDate:"'+startDate+'" includeComponentsForFeeTypes:[FBA_STORAGE_FEE]aggregateBy:{date:MONTH}){fees{charge{aggregatedDetail{totalAmount{amount}}properties{propertyName propertyValue}}charges{components{properties{propertyName propertyValue}aggregatedDetail{amount{amount}amountPerUnit{amount}amountPerUnitDelta{amount}promotionAmount{amount}totalAmount{amount}taxAmount{amount}}name}aggregatedDetail{amount{amount}amountPerUnit{amount}amountPerUnitDelta{amount}promotionAmount{amount}taxAmount{amount}totalAmount{amount}quantity}}}fnsku msku parentAsin childAsin cost{mfnCost{storageCost{amount currencyCode}}miscellaneousCost{amount currencyCode}}}}}'
            reports.append(AmazonDataKioskReport(reporttype=DataKioskType.ECONOMICS, req=DataKioskCreateQueryRequest(body=DataKioskCreateQuerySpecification(query=query))))
        return reports
        return reports

    async def __createReport(self, req: DataKioskCreateQueryRequest)-> str|None:
        try:
            return (await self.spapi.datakiosk.create_query(req)).queryId
        except DzgroError as e:
            if e.status_code==429:
                self.createThrottle = True
                return None
            raise e
        
    async def __getReport(self, query_id: str) -> DataKioskQueryResponse|None:
        try:
            if not query_id: return None
            return (await self.spapi.datakiosk.get_query(query_id))
        except DzgroError as e:
            if e.status_code==429:
                self.getThrottle = True
                return None
            raise e

    async def __getDocument(self, document_id: str) -> DataKioskDocumentResponse|None:
        try:
            if not document_id: return None
            return (await self.spapi.datakiosk.get_query_result_document(document_id))
        except DzgroError as e:
            if e.status_code==429:
                self.getDocumentThrottle = True
                return None
            raise e
    
    async def __processDataKioskReport(self, report: AmazonDataKioskReportDB)->tuple[AmazonDataKioskReportDB, bool]:
        query_id: str|None = report.res.queryId if report.res else None
        data_document_id: str|None = report.res.dataDocumentId if report.res else None
        try:
            if not query_id and report.req and not self.createThrottle: 
                query_id = (await self.__createReport(report.req))
                if query_id: report.res = await self.__getReport(query_id)
            if report.res and report.res.processingStatus == ProcessingStatus.FATAL and report.res.errorDocumentId:
                    doc = await self.__getDocument(report.res.errorDocumentId)
                    if doc: error = await self.reportUtil.fetchData(doc.documentUrl, False)
                    else: error = "Report processing failed"
                    raise DzgroError(errors=ErrorList(errors=[ErrorDetail(code=500, message="Report processing failed", details=error)]))
            if query_id and (not report.res or data_document_id is None) and not self.getThrottle: report.res = await self.__getReport(query_id)
            elif report.res:
                if report.res.processingStatus==ProcessingStatus.DONE:
                    if report.res.dataDocumentId: report.document = await self.__getDocument(report.res.dataDocumentId)
            return report, True
        except DzgroError as e:
            raise e
        except Exception as e:
            error = ErrorDetail(code=500, message="Some Error Occurred", details=str(e))
            raise DzgroError(errors=ErrorList(errors=[error]), status_code=500)

    async def processDataKioskReports(self, reports: list[AmazonDataKioskReportDB], reportUtil: ReportUtil, reportId: PyObjectId)->bool:
        self.reportUtil = reportUtil
        self.reportId = reportId
        shouldContinue = True
        hasError = False
        for report in reports:
            processedReport = report.__deepcopy__()
            if shouldContinue and not report.filepath:
                try:
                    processedReport, shouldContinue = await self.__processDataKioskReport(processedReport)
                    if processedReport.res:
                        if processedReport.res.processingStatus==ProcessingStatus.CANCELLED: processedReport.filepath = 'No Data Available'
                        elif processedReport.res.processingStatus==ProcessingStatus.FATAL: processedReport.error = ErrorList(errors=[ErrorDetail(code=500, message="Report processing failed", details=f"Report {processedReport.res.queryId} is in {processedReport.res.processingStatus.value} status")])
                        elif processedReport.document and processedReport.req:
                            key = f'kiosk/{id}'
                            dataStr, processedReport.filepath = await reportUtil.insertToS3(key, processedReport.document.documentUrl, False)
                            await self.__saveData(dataStr, processedReport.reporttype)
                except DzgroError as e:
                    processedReport.error = e.errors
                    shouldContinue = False
                    hasError = True
                if report.model_dump() != processedReport.model_dump():
                    shouldContinue = processedReport.error is None
                    await self.client.db.amazon_daily_reports.updateChildReport(processedReport.id, processedReport.model_dump(exclude_none=True, exclude_defaults=True, by_alias=True))
        return not hasError

    def __convertDataKioskFileToList(self, dataStr: str)->list[dict]:
        data: list[dict] = []
        for line in dataStr.splitlines():
            lineAsDict = json.loads(line)
            data.append(lineAsDict)
        return data

    async def __saveData(self, datastr:str, reporttype: DataKioskType):
        if reporttype==DataKioskType.SALES_TRAFFIC_ASIN:
            return await self.__convertTrafficReport(datastr)
        else: 
            return await self.__convertEconomicsReport(datastr)

    async def __convertTrafficReport(self, dataStr: str):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.datakiosk.TrafficReportConvertor import TrafficReportConvertor
        data = self.__convertDataKioskFileToList(dataStr)
        trafficConvertor = TrafficReportConvertor(self.marketplace)
        trafficSkus = trafficConvertor.convertTrafficData(data)
        await self.reportUtil.update(CollectionType.TRAFFIC, trafficSkus, self.reportId)

    async def __convertEconomicsReport(self, dataStr: str):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.datakiosk.TrafficReportConvertor import TrafficReportConvertor
        data = self.__convertDataKioskFileToList(dataStr)
        trafficConvertor = TrafficReportConvertor(self.marketplace)
        trafficSkus = trafficConvertor.convertTrafficData(data)
        await self.reportUtil.update(CollectionType.TRAFFIC, trafficSkus, self.reportId)
