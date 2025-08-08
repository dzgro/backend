import json
from amazon_daily_report.reports.ReportUtils import ReportUtil
from amazonapi.spapi import SpApiClient
from datetime import datetime
from bson import ObjectId
from db import DbClient
from models.amazonapi.errors import APIError
from models.amazonapi.spapi.reports import ProcessingStatus, SPAPICreateReportSpecification
from models.extras.amazon_daily_report import AmazonSpapiReport, AmazonSpapiReportDB, MarketplaceObjectForReport, PyObjectId, SPAPIReport,SPAPIReportDocument
from models.enums import AmazonReportType, CollectionType, SPAPIReportType
from amazon_daily_report.reports import Utility
from models.model import ErrorDetail, ErrorList

class AmazonSpapiReportManager:
    spapi: SpApiClient
    timezone: str
    createThrottle: bool = False
    getThrottle: bool = False
    getDocumentThrottle: bool = False
    reportUtil: ReportUtil
    dbClient: DbClient
    reportId: PyObjectId


    def __init__(self, marketplace: MarketplaceObjectForReport, spapi: SpApiClient) -> None:
        self.spapi = spapi
        self.timezone = marketplace.details.timezone
        self.marketplace = marketplace

    def __getattr__(self, item):
        return None

    async def getSPAPIReportsConf(self, startdate: datetime, months: int)->list[AmazonSpapiReport]:
        reports: list[AmazonSpapiReport] = await self.__getSettlementReports(startdate)
        dates = Utility.getConfDatesByMonths(months, self.timezone, 'spapi', 30)
        reports.append(self.__createSPAPIReportConf(reportType=SPAPIReportType.GET_V2_SELLER_PERFORMANCE_REPORT))
        reports.append(self.__createSPAPIReportConf(reportType=SPAPIReportType.GET_MERCHANT_LISTINGS_ALL_DATA))
        for date in dates:
            reports.append(self.__createSPAPIReportConf(reportType=SPAPIReportType.GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL, startDate=date[0], endDate=date[1]))
        return reports
    
    async def __getSettlementReports(self, startdate:datetime):
        reports =  (await self.spapi.reports.get_reports(
            report_types=['GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2'],
            created_since=startdate
        )).reports
        return [AmazonSpapiReport(res=report) for report in reports]

    def __createSPAPIReportConf(self, reportType: SPAPIReportType, startDate: datetime|None=None, endDate: datetime|None=None):
        req = SPAPICreateReportSpecification(
            reportType=reportType,
            marketplaceIds=[self.spapi.object.marketplaceid]
        )
        if startDate: req.data_start_time = startDate
        if endDate: req.data_end_time = endDate
        return AmazonSpapiReport( req=req )

    async def __createReport(self, req: SPAPICreateReportSpecification) -> str|None:
        try:
            if self.createThrottle: return None
            return (await self.spapi.reports.create_report(req)).report_id
        except APIError as e:
            if e.status_code==429:
                self.createThrottle = True
                return None
            raise e


        
    async def __getReport(self, reportid: str) -> SPAPIReport|None:
        try:
            if self.getThrottle: return None
            return await self.spapi.reports.get_report(reportid)
        except APIError as e:
            if e.status_code==429:
                self.getThrottle = True
                return None
            raise e
        
    async def __getDocument(self, reportDocid: str) -> SPAPIReportDocument|None:
        try:
            if self.getDocumentThrottle: return None
            return await self.spapi.reports.get_report_document(reportDocid)
        except APIError as e:
            if e.status_code==429:
                self.getDocumentThrottle = True
                return None
            raise e
        
    async def processSpapiReports(self, reports: list[AmazonSpapiReportDB], reportUtil: ReportUtil, dbClient: DbClient, reportId: PyObjectId) -> bool:
        self.reportUtil = reportUtil
        self.dbClient = dbClient
        self.reportId = reportId
        db = self.dbClient.amazon_daily_reports(self.marketplace.uid, ObjectId(str(self.marketplace.id)))
        shouldContinue = True
        isListingFileProcessed = False
        for report in reports:
            if shouldContinue and not report.filepath:
                try:
                    processedReport, shouldContinue = await self.__processSpapiReport(report)
                    if processedReport.document and processedReport.req: 
                        key = f'spapi/{processedReport.req.report_type}/{id}'
                        dataStr, processedReport.filepath = reportUtil.insertToS3(key, processedReport.document.url, processedReport.document.compression_algorithm is not None)
                        await self.__addSPAPIReport(dataStr, processedReport.req.report_type)
                except APIError as e:
                    processedReport.error = e.error_list
                if report.model_dump() != processedReport.model_dump():
                    await db.updateChildReport(processedReport.id, processedReport.model_dump(exclude_none=True, exclude_defaults=True))
                    if not isListingFileProcessed and report.req and report.req.report_type == SPAPIReportType.GET_MERCHANT_LISTINGS_ALL_DATA:
                        isListingFileProcessed = True
        return isListingFileProcessed

    def __convertSPAPIFileToList(self, dataStr: str)->list[dict]:
        lines = [line.split('\t') for line in dataStr.splitlines()]
        data: list[dict] = []
        try: return [{header: line[index] for index,header in enumerate(lines[0])} for line in lines[1:]]
        except: return data

    async def __addSPAPIReport(self, dataStr: str, reportType: SPAPIReportType):
        if reportType==SPAPIReportType.GET_V2_SELLER_PERFORMANCE_REPORT: 
            await self.__executeHealthReport(dataStr)
        else:
            data = self.__convertSPAPIFileToList(dataStr)
            if reportType==SPAPIReportType.GET_MERCHANT_LISTINGS_ALL_DATA: await self.__executeListings(data)
            elif reportType==SPAPIReportType.GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2: await self.__executeSettlementReports(data)
            elif reportType==SPAPIReportType.GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL: await self.__executeOrderReports(data)

    async def __executeHealthReport(self, data: str):
        from amazon_daily_report.reports.report_types.spapi.HealthReportConvertor import HealthReportConvertor
        report = HealthReportConvertor(self.marketplace).convertToReport(json.loads(data))
        await self.reportUtil.update(self.dbClient, CollectionType.HEALTH, [{'health': report.model_dump(exclude_none=True), '_id': self.marketplace.id}], self.reportId)

    async def __executeOrderReports(self, data: list[dict]):
        from amazon_daily_report.reports.report_types.spapi.OrderReportConvertor import OrderReportConvertor
        convertor = OrderReportConvertor(self.marketplace, self.spapi)
        orders, orderItems = convertor.convert(data)
        await self.reportUtil.update(self.dbClient, CollectionType.ORDERS, [item.model_dump(exclude_none=True, by_alias=True) for item in orders], self.reportId)
        orderIdsList = list(map(lambda x: f'{str(self.marketplace.id)}_{x.orderid}', orders))
        await self.dbClient.order_items(self.marketplace.uid, ObjectId(str(self.marketplace.id))).deleteOrderItems(orderIdsList)
        await self.reportUtil.update(self.dbClient, CollectionType.ORDER_ITEMS, [item.model_dump(exclude_none=True) for item in orderItems], None)
        if convertor.hasIndiaCountry: await self.dbClient.orders(self.marketplace.uid, ObjectId(str(self.marketplace.id))).replaceStateNames()

    async def __executeSettlementReports(self, data: list[dict]):
        from amazon_daily_report.reports.report_types.spapi.SettlementReportConvertor import SettlementReportConvertor
        helper = self.dbClient.settlements(self.marketplace.uid, ObjectId(str(self.marketplace.id)))
        settlementIds = await helper.getSettlementIds()
        settlements = SettlementReportConvertor().convert(data, settlementIds)
        await self.reportUtil.update(self.dbClient, CollectionType.SETTLEMENTS, [item.model_dump(exclude_none=True, by_alias=True) for item in settlements], None)

    async def __executeListings(self, data: list[dict]):
        from amazon_daily_report.reports.report_types.spapi.ListingReportConvertor import ListingReportConvertor
        listings = ListingReportConvertor(self.marketplace).addListings(data)
        await self.reportUtil.update(self.dbClient, CollectionType.PRODUCTS, listings, self.reportId)

    async def __processSpapiReport(self, report: AmazonSpapiReportDB)->tuple[AmazonSpapiReportDB, bool]:
        reportid: str|None = report.res.report_id if report.res else None
        reportDocId: str|None = report.res.report_document_id if report.res else None
        try:
            if not reportid and report.req: reportid = (await self.__createReport(report.req))
            if reportid and not report.res: report.res = await self.__getReport(reportid)
            else:
                if reportid is not None and reportDocId is None: 
                    report.res = await self.__getReport(reportid)
                    if report.res:
                        if report.res.processing_status==ProcessingStatus.DONE:
                            if report.res.report_document_id and report.req: 
                                report.document = await self.__getDocument(report.res.report_document_id)
                        elif report.res.processing_status == ProcessingStatus.FATAL:
                            raise APIError(error_list=ErrorList(errors=[ErrorDetail(code=500, message="Report processing failed", details=f"Report {reportid} is in {report.res.processing_status} status")]))
            return report, True
        except APIError as e:
            raise e
        except Exception as e:
            error = ErrorDetail(code=500, message="Some Error Occurred", details=str(e))
            raise APIError(error_list=ErrorList(errors=[error]), status_code=500)