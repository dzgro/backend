import json
from amazon_daily_report.reports.ReportUtils import ReportUtil
from amazonapi.client import APIError
from amazonapi.spapi import SpApiClient
from bson import ObjectId
from db import DbClient
from models.amazonapi.spapi.datakiosk import DataKioskCreateQueryRequest, DataKioskQueryResponse, DataKioskDocumentResponse, DataKioskCreateQuerySpecification
from models.amazonapi.spapi.reports import ProcessingStatus
from models.enums import CollectionType
from models.extras.amazon_daily_report import AmazonDataKioskReport, AmazonDataKioskReportDB, MarketplaceObjectForReport
from amazon_daily_report.reports import Utility
from models.model import ErrorDetail, ErrorList, PyObjectId

class AmazonDataKioskReportManager:
    spapi: SpApiClient
    timezone: str
    createThrottle: bool = False
    getThrottle: bool = False
    getDocumentThrottle: bool = False
    marketplace: MarketplaceObjectForReport
    reportUtil: ReportUtil
    dbClient: DbClient
    reportId: PyObjectId


    def __init__(self, marketplace: MarketplaceObjectForReport, spapi: SpApiClient) -> None:
        self.spapi = spapi
        self.timezone = marketplace.details.timezone
        self.marketplace = marketplace

    def getDataKioskReportsConf(self,months:int)->list[AmazonDataKioskReport]:
        reports: list[AmazonDataKioskReport] = []
        reports.extend(self.__getAsinTrafficReportsConf(months))
        # reports.extend(self.getSkuEconomicsConf(months, endDate))
        return reports 

    def __getAsinTrafficReportsConf(self, months: int)->list[AmazonDataKioskReport]:
        dates = Utility.getConfDatesByMonths(months, self.timezone, 'kiosk', 1)
        reports: list[AmazonDataKioskReport] = []
        dateFormat =  "%Y-%m-%d"
        for date in dates:
            startDate, endDate = date
            query = 'query MyQuery{analytics_salesAndTraffic_2024_04_24{salesAndTrafficByAsin(aggregateBy:PARENT endDate:"'+endDate.strftime(dateFormat)+'" marketplaceIds:["'+self.spapi.object.marketplaceid+'"] startDate:"'+startDate.strftime(dateFormat)+'"){childAsin endDate marketplaceId parentAsin sales{orderedProductSales{amount currencyCode}orderedProductSalesB2B{amount currencyCode}totalOrderItems totalOrderItemsB2B unitsOrdered unitsOrderedB2B}sku startDate traffic{browserPageViews browserPageViewsB2B browserPageViewsPercentage browserPageViewsPercentageB2B browserSessionPercentage browserSessions browserSessionPercentageB2B browserSessionsB2B buyBoxPercentage buyBoxPercentageB2B mobileAppPageViews mobileAppPageViewsPercentage mobileAppPageViewsB2B mobileAppPageViewsPercentageB2B mobileAppSessionPercentageB2B mobileAppSessionPercentage mobileAppSessions mobileAppSessionsB2B pageViews pageViewsB2B pageViewsPercentage pageViewsPercentageB2B sessionPercentage sessionPercentageB2B sessions sessionsB2B unitSessionPercentage unitSessionPercentageB2B}}}}'
            reports.append(AmazonDataKioskReport(req=DataKioskCreateQueryRequest(body=DataKioskCreateQuerySpecification(query=query))))
        return reports

    async def __createReport(self, req: DataKioskCreateQueryRequest)-> str|None:
        try:
            return (await self.spapi.datakiosk.create_query(req)).queryId
        except APIError as e:
            if e.status_code==429:
                self.createThrottle = True
                return None
            raise e
        
    async def __getReport(self, query_id: str) -> DataKioskQueryResponse|None:
        try:
            if not query_id: return None
            return (await self.spapi.datakiosk.get_query(query_id))
        except APIError as e:
            if e.status_code==429:
                self.getThrottle = True
                return None
            raise e

    async def __getDocument(self, document_id: str) -> DataKioskDocumentResponse|None:
        try:
            if not document_id: return None
            return (await self.spapi.datakiosk.get_query_result_document(document_id))
        except APIError as e:
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
            if query_id and (not report.res or data_document_id is None) and not self.getThrottle: report.res = await self.__getReport(query_id)
            elif report.res:
                if report.res.processingStatus==ProcessingStatus.DONE:
                    if report.res.dataDocumentId: report.document = await self.__getDocument(report.res.dataDocumentId)
                elif report.res.processingStatus == ProcessingStatus.FATAL or report.res.errorDocumentId is not None:
                    raise APIError(error_list=ErrorList(errors=[ErrorDetail(code=500, message="Report processing failed", details=f"Report {query_id} is in Fatal status")]))
            return report, True
        except APIError as e:
            raise e
        except Exception as e:
            error = ErrorDetail(code=500, message="Some Error Occurred", details=str(e))
            raise APIError(error_list=ErrorList(errors=[error]), status_code=500)

    async def processDataKioskReports(self, reports: list[AmazonDataKioskReportDB], reportUtil: ReportUtil, dbClient: DbClient, reportId: PyObjectId):
        self.reportUtil = reportUtil
        self.dbClient = dbClient
        self.reportId = reportId
        db = self.dbClient.amazon_daily_reports(self.marketplace.uid, ObjectId(str(self.marketplace.id)))
        shouldContinue = True
        for index, report in enumerate(reports):
            processedReport = report.__deepcopy__()
            if shouldContinue and not report.filepath:
                try:
                    processedReport, shouldContinue = await self.__processDataKioskReport(processedReport)
                    if processedReport.document and processedReport.req: 
                        key = f'kiosk/{id}'
                        dataStr, processedReport.filepath = reportUtil.insertToS3(key, processedReport.document.documentUrl, False)
                        await self.__convertTrafficReport(dataStr)
                except APIError as e:
                    processedReport.error = e.error_list
                if report.model_dump() != processedReport.model_dump():
                    await db.updateChildReport(processedReport.id, processedReport.model_dump(exclude_none=True, exclude_defaults=True, by_alias=True))

    def __convertDataKioskFileToList(self, dataStr: str)->list[dict]:
        data: list[dict] = []
        for line in dataStr.splitlines():
            lineAsDict = json.loads(line)
            data.append(lineAsDict)
        return data

    async def __convertTrafficReport(self, dataStr: str):
        from amazon_daily_report.reports.report_types.datakiosk.TrafficReportConvertor import TrafficReportConvertor
        data = self.__convertDataKioskFileToList(dataStr)
        trafficConvertor = TrafficReportConvertor(self.marketplace)
        trafficSkus = trafficConvertor.convertTrafficData(data)
        await self.reportUtil.update(self.dbClient, CollectionType.TRAFFIC, trafficSkus, self.reportId)
