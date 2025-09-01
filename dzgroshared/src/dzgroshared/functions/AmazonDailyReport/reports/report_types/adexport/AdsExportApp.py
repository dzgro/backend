from dzgroshared.client import DzgroSharedClient
from dzgroshared.functions.AmazonDailyReport.reports.ReportUtils import ReportUtil
from dzgroshared.amazonapi.adapi import AdApiClient
import json
from dzgroshared.models.amazonapi.adapi.common.exports import ExportRequest, ExportResponse, ExportStatus
from dzgroshared.models.model import DzgroError
from dzgroshared.models.extras.amazon_daily_report import AmazonExportReport, AmazonAdExportDB, MarketplaceObjectForReport
from dzgroshared.models.enums import AdExportType, AdProduct, AdReportType, AdState, CollectionType
from dzgroshared.models.model import ErrorDetail, ErrorList, PyObjectId


class AmazonAdsExportManager:
    client: DzgroSharedClient
    api: AdApiClient
    createThrottle: bool = False
    getThrottle: bool = False
    marketplace: MarketplaceObjectForReport
    reportUtil: ReportUtil
    reportId: PyObjectId

    def __init__(self, client: DzgroSharedClient, marketplace: MarketplaceObjectForReport, api: AdApiClient) -> None:
        self.client = client
        self.api = api
        self.marketplace = marketplace

    async def createExports(self)->list[AmazonExportReport]:
        
        return  [
            AmazonExportReport(exportType=AdExportType.CAMPAIGN),
            AmazonExportReport(exportType=AdExportType.AD),
            AmazonExportReport(exportType=AdExportType.AD_GROUP),
            AmazonExportReport(exportType=AdExportType.TARGET)
        ]
    
    async def createExport(self, req: AmazonAdExportDB) -> AmazonAdExportDB|None:
        req.req=ExportRequest( stateFilter=AdState.values(), adProductFilter= AdProduct.values())
        try:
            if self.createThrottle: return req
            if req.exportType == AdExportType.CAMPAIGN:
                req.res =  await self.api.common.exportsClient.export_campaigns(req.req)
            elif req.exportType == AdExportType.AD:
                req.res =  await self.api.common.exportsClient.export_ads(req.req)
            elif req.exportType == AdExportType.AD_GROUP:
                req.res =  await self.api.common.exportsClient.export_ad_groups(req.req)
            elif req.exportType == AdExportType.TARGET:
                req.res =  await self.api.common.exportsClient.export_targets(req.req)
            return req
        except DzgroError as e:
            if e.status_code==429:
                self.createThrottle = True
                return None
            raise e
    
    async def getExport(self, exportType: AdExportType, exportId:str) -> ExportResponse|None:
        try:
            if exportType == AdExportType.CAMPAIGN:
                return await self.api.common.exportsClient.get_campaign_export_status(exportId)
            elif exportType == AdExportType.AD:
                return await self.api.common.exportsClient.get_ads_export_status(exportId)
            elif exportType == AdExportType.AD_GROUP:
                return await self.api.common.exportsClient.get_adgroup_export_status(exportId)
            elif exportType == AdExportType.TARGET:
                return await self.api.common.exportsClient.get_targets_export_status(exportId)
        except DzgroError as e:
            if e.status_code==429:
                self.getThrottle = True
                return None
            raise e
    
    async def __processAdExport(self, report: AmazonAdExportDB)->tuple[AmazonAdExportDB, bool]:
        try:
            if not report.res:
                if not self.createThrottle:
                    report = (await self.createExport(report)) or report
                return report, not self.createThrottle
            else:
                if not self.getThrottle:
                    report.res = (await self.getExport(report.exportType, report.res.exportId)) or report.res
                return report, not self.getThrottle
        except DzgroError as e:
            raise e
        except Exception as e:
            error = ErrorDetail(code=500, message="Some Error Occurred", details=str(e))
            raise DzgroError(error_list=ErrorList(errors=[error]), status_code=500)

    async def processExportReports(self, reports: list[AmazonAdExportDB], reportUtil: ReportUtil, reportId: PyObjectId)->bool:
        self.reportUtil = reportUtil
        self.reportId = reportId
        shouldContinue = True
        hasError = False
        for report in reports:
            processedReport = report.__deepcopy__()
            if shouldContinue and not report.filepath:
                try:
                    processedReport, shouldContinue = await self.__processAdExport(processedReport)
                    if processedReport.res:
                        if processedReport.res.status==ExportStatus.FAILED: processedReport.error = ErrorList(errors=[ErrorDetail(code=500, message="Report processing failed", details=f"Report {processedReport.res.exportId} is in {processedReport.res.status.value} status")])
                        elif processedReport.res.url and processedReport.req:
                            key = f'adexport/{report.exportType.value}/{processedReport.res.exportId}'
                            dataStr, processedReport.filepath = await reportUtil.insertToS3(key, processedReport.res.url, True)
                            await self.__convertExportReport(report.exportType, dataStr)
                except DzgroError as e:
                    processedReport.error = e.error_list
                    shouldContinue = False
                    hasError = True
                if report.model_dump() != processedReport.model_dump():
                    shouldContinue = processedReport.error is None
                    await self.client.db.amazon_daily_reports.updateChildReport(processedReport.id, processedReport.model_dump(exclude_none=True, exclude_defaults=True, by_alias=True))
        return not hasError

    def __convertExportFileToList(self, dataStr: str)->list[dict]:
        data: list[dict] = []
        for line in json.loads(dataStr):
            lineAsDict = json.loads(line)
            data.append(lineAsDict)
        return data

    async def __convertExportReport(self, exportType: AdExportType, dataStr: str):
        from dzgroshared.functions.AmazonDailyReport.reports.report_types.adexport.AdsExportConvertor import AdsExportConvertor
        data = json.loads(dataStr)
        exports = AdsExportConvertor().getExportData(exportType, data, str(self.marketplace.id))
        await self.reportUtil.update(CollectionType.ADV_ASSETS, exports, self.reportId)
