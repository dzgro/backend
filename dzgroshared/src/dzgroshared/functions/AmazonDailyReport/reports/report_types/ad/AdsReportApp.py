from dzgroshared.functions import FunctionClient
from dzgroshared.functions.AmazonDailyReport.reports.ReportUtils import ReportUtil
from dzgroshared.amazonapi.adapi import AdApiClient
from dzgroshared.utils.date_util import DateHelper
from datetime import datetime
import json
from dzgroshared.models.amazonapi.adapi.common.reports import AdReport, AdReportConfiguration, AdReportRequest, ReportStatus, TimeUnit, ReportFormat
from dzgroshared.models.amazonapi.errors import APIError
from dzgroshared.models.extras.amazon_daily_report import AmazonAdReport, AmazonAdReportDB, MarketplaceObjectForReport
from dzgroshared.models.enums import AdProduct, AdReportType, CollectionType
from dzgroshared.models.model import ErrorDetail, ErrorList, PyObjectId


class AmazonAdsReportManager:
    fnClient: FunctionClient
    helper: DateHelper
    dateFormat = "%Y-%m-%d"
    createThrottle: bool = False
    getThrottle: bool = False
    marketplace: MarketplaceObjectForReport
    reportUtil: ReportUtil
    reportId: PyObjectId

    def __init__(self, fnClient: FunctionClient, marketplace: MarketplaceObjectForReport, api: AdApiClient) -> None:
        self.fnClient = fnClient
        self.api = api
        self.helper = DateHelper()
        self.timezone = marketplace.details.timezone
        self.marketplace = marketplace

    def getReportsConf(self, months: int)->list[AmazonAdReport]:
        reports: list[AmazonAdReport] = []
        reports.extend(self.__createCampaignReports(months))
        reports.extend(self.__createSearchTermReports(months))
        reports.extend(self.__createTargetingReports(months))
        reports.extend(self.__createAdvertisedProductReports(months))
        return reports

    def __createReportConf(self, startDate: datetime,endDate: datetime, conf: AdReportConfiguration)->AmazonAdReport:
        endDateString = self.helper.convertToString(endDate, self.dateFormat)
        startDateString = self.helper.convertToString(startDate, self.dateFormat)
        return AmazonAdReport(req=AdReportRequest(
            startDate=startDateString,
            endDate=endDateString,
            configuration=conf
        ))
    
    def __createReportConfByType(self, months: int, conf: AdReportConfiguration, allowedDuration:int):
        from dzgroshared.functions.AmazonDailyReport.reports import Utility
        dates = Utility.getConfDatesByMonths(months, self.timezone, 'ad', allowedDuration)
        return [self.__createReportConf(date[0], date[1], conf) for date in dates]

    def __createCampaignReports(self, months: int)->list[AmazonAdReport]:
        def createSPCampaignReport():
            columns: list[str] = ["campaignId","date","impressions","clicks","cost","purchases14d","unitsSoldClicks14d", "sales14d","placementClassification","topOfSearchImpressionShare"]
            groupBy: list[str] = ["campaignPlacement"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SP, reportTypeId=AdReportType.SPCAMPAIGNS, columns=columns, groupBy=groupBy, timeUnit=TimeUnit.DAILY, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)

        def createSBCampaignReport():
            columns: list[str] = ["campaignId","date","impressions","clicks","cost","unitsSold","sales","purchases","newToBrandPurchases","newToBrandSales","viewableImpressions","videoFirstQuartileViews","videoMidpointViews","videoThirdQuartileViews","videoUnmutes"]
            groupBy: list[str] = ["campaign"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SB, reportTypeId=AdReportType.SBCAMPAIGNS, columns=columns, groupBy=groupBy, timeUnit=TimeUnit.DAILY, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)

        def createSDCampaignReport():
            columns: list[str] = ["campaignId","date","impressions","clicks","cost","unitsSold","sales","purchases","newToBrandPurchases","newToBrandSales", "impressionsViews","videoFirstQuartileViews","videoMidpointViews","videoThirdQuartileViews","videoCompleteViews","videoUnmutes"]
            groupBy: list[str] = ["campaign"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SD, reportTypeId=AdReportType.SDCAMPAIGNS, columns=columns, groupBy=groupBy, timeUnit=TimeUnit.DAILY, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)

        reports: list[AmazonAdReport] = []
        reports.extend(createSPCampaignReport())
        reports.extend(createSBCampaignReport())
        reports.extend(createSDCampaignReport())
        return list(filter(lambda x: x is not None, reports))


    def __createSearchTermReports(self, months: int)->list[AmazonAdReport]:
        def createSPSearchTermReport():
            columns: list[str] = ["adGroupId","date", "targeting", "matchType","impressions","unitsSoldClicks14d","clicks","cost","purchases14d","sales14d","searchTerm"]
            groupBy: list[str]=["searchTerm"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SP, reportTypeId=AdReportType.SPSEARCHTERM, columns=columns, timeUnit=TimeUnit.DAILY, groupBy=groupBy, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)
        
        def createSBSearchTermReport():
            columns: list[str] = ["adGroupId","date", "keywordType","keywordId","matchType","impressions","viewableImpressions","unitsSold","purchases","clicks","cost","sales","searchTerm","videoFirstQuartileViews","videoMidpointViews","videoThirdQuartileViews","videoUnmutes"]
            groupBy: list[str]=["searchTerm"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SB, reportTypeId=AdReportType.SBSEARCHTERM, columns=columns, timeUnit=TimeUnit.DAILY, groupBy=groupBy, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)

        reports: list[AmazonAdReport] = []
        reports.extend(createSPSearchTermReport())
        # reports.append(createSBSearchTermReport(startDate,endDate))
        return reports
    


    def __createTargetingReports(self, months: int)->list[AmazonAdReport]:
        def createSPTargetingReport():
            columns: list[str] = ["adGroupId","date","keywordId","impressions","clicks","unitsSoldClicks14d","cost","purchases14d","sales14d","targeting","matchType", "topOfSearchImpressionShare"]
            groupBy: list[str]=["targeting"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SP, reportTypeId=AdReportType.SPTARGETING, columns=columns, timeUnit=TimeUnit.DAILY, groupBy=groupBy, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)
        reports: list[AmazonAdReport] = []
        reports.extend(createSPTargetingReport())
        return reports

    def __createAdvertisedProductReports(self, months: int)->list[AmazonAdReport]:
        def createSPAdvertisedProductReport():
            columns: list[str] = ["adGroupId","date","adId","advertisedAsin","advertisedSku","unitsSoldClicks14d","impressions","clicks","cost","purchases14d","sales14d"]
            groupBy: list[str]=["advertiser"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SP, reportTypeId=AdReportType.SPADVERTISEDPRODUCT, columns=columns, timeUnit=TimeUnit.DAILY, groupBy=groupBy, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)
        def createSDAdvertisedProductReport():
            columns: list[str] = ["adGroupId","date","adId","promotedAsin","promotedSku","unitsSold","impressions","impressionsViews", "clicks","cost","purchases","sales","videoFirstQuartileViews","videoMidpointViews","videoThirdQuartileViews","videoCompleteViews","videoUnmutes"]
            groupBy: list[str]=["advertiser"]
            configuration=AdReportConfiguration(adProduct=AdProduct.SD, reportTypeId=AdReportType.SDADVERTISEDPRODUCT, columns=columns, timeUnit=TimeUnit.DAILY, groupBy=groupBy, format=ReportFormat.GZIP_JSON)
            return self.__createReportConfByType(months, configuration, 30)
        reports: list[AmazonAdReport] = []
        reports.extend(createSPAdvertisedProductReport())
        reports.extend(createSDAdvertisedProductReport())
        return reports

    async def __createReport(self, req: AdReportRequest) -> AdReport|None:
        try:
            if self.createThrottle: return None
            return (await self.api.common.reportClient.create_report(req))
        except APIError as e:
            if e.status_code==425 and e.error_list.errors[0].details:
                reportid = json.loads(e.error_list.errors[0].details)['detail'].split(':')[1].strip()
                return await self.__getReport(reportid)
            if e.status_code==429:
                self.createThrottle = True
                return None

    async def __getReport(self, reportId: str) -> AdReport|None:
        try:
            if self.getThrottle: return None
            return await self.api.common.reportClient.get_report(reportId)
        except APIError as e:
            if e.status_code==429:
                self.getThrottle = True
                return None
            raise e

    async def __processAdReport(self, report: AmazonAdReportDB)->tuple[AmazonAdReportDB, bool]:
        reportid: str|None = report.res.reportId if report.res else None
        try:
            if not reportid and report.req: report.res = (await self.__createReport(report.req))
            if reportid: 
                report.res = await self.__getReport(reportid)
                if report.res:
                    if report.res.status==ReportStatus.FAILED:
                        raise APIError(error_list=ErrorList(errors=[ErrorDetail(code=500, message="Report processing failed", details=f"Report {reportid} is in Failed status")]))
            return report, True
        except APIError as e:
            raise e
        except Exception as e:
            error = ErrorDetail(code=500, message="Some Error Occurred", details=str(e))
            raise APIError(error_list=ErrorList(errors=[error]), status_code=500)
        
    async def processAdReports(self, reports: list[AmazonAdReportDB], reportUtil: ReportUtil, reportId: PyObjectId):
        self.reportUtil = reportUtil
        self.reportId = reportId
        shouldContinue = True
        for report in reports:
            processedReport = report.__deepcopy__()
            if shouldContinue and not report.filepath:
                try:
                    processedReport, shouldContinue = await self.__processAdReport(processedReport)
                    if processedReport.req and processedReport.res and processedReport.res.url: 
                        key = f'ad/{processedReport.req.configuration.reportTypeId}/{processedReport.res.reportId}'
                        dataStr, processedReport.filepath = reportUtil.insertToS3(key, processedReport.res.url, True)
                        await self.__convertAdReport(processedReport.req.configuration.reportTypeId, dataStr)
                except APIError as e:
                    processedReport.error = e.error_list
                if report.model_dump() != processedReport.model_dump():
                    await self.fnClient.client.db.amazon_daily_reports.updateChildReport(processedReport.id, processedReport.model_dump(exclude_none=True, exclude_defaults=True, by_alias=True))

    def __convertExportFileToList(self, dataStr: str)->list[dict]:
        return json.loads(dataStr)

    async def __convertAdReport(self, reportType: AdReportType, dataStr: str):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.ad.AdsReportConvertor import AdsReportConvertor
        convertor = AdsReportConvertor(self.marketplace.id)
        data = convertor.getAdReportData(reportType, self.__convertExportFileToList(dataStr))
        await self.reportUtil.update(self.fnClient.client.db, CollectionType.ADV, data, self.reportId)
    
    


