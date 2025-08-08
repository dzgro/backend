from amazon_daily_report.reports.ReportUtils import ReportUtil
from amazonapi.adapi import AdApiClient
from bson import ObjectId
from date_util import Literal
from date_util import DateHelper
from datetime import datetime
import json

from db import DbClient
from models.amazonapi.adapi.common.exports import ExportRequest, ExportResponse
from models.amazonapi.errors import APIError
from models.extras.amazon_daily_report import AmazonExportReport, AmazonAdExportDB, MarketplaceObjectForReport
from models.enums import AdExportType, AdProduct, AdReportType, AdState, CollectionType
from models.model import ErrorDetail, ErrorList, PyObjectId


class AmazonAdsExportManager:
    api: AdApiClient
    createThrottle: bool = False
    getThrottle: bool = False
    marketplace: MarketplaceObjectForReport
    reportUtil: ReportUtil
    dbClient: DbClient
    reportId: PyObjectId

    def __init__(self, marketplace: MarketplaceObjectForReport, api: AdApiClient) -> None:
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
        except APIError as e:
            if e.status_code==429:
                self.createThrottle = True
                return None
            raise e
    
    async def getExport(self, exportId: str) -> ExportResponse|None:
        try:
            return await self.api.common.exportsClient.get_campaign_export_status(exportId)
        except APIError as e:
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
                    report.res = (await self.getExport(report.res.exportId)) or report.res
                return report, not self.getThrottle
        except APIError as e:
            raise e
        except Exception as e:
            error = ErrorDetail(code=500, message="Some Error Occurred", details=str(e))
            raise APIError(error_list=ErrorList(errors=[error]), status_code=500)

    async def processExportReports(self, reports: list[AmazonAdExportDB], reportUtil: ReportUtil, dbClient: DbClient, reportId: PyObjectId):
        self.reportUtil = reportUtil
        self.dbClient = dbClient
        self.reportId = reportId
        db = self.dbClient.amazon_daily_reports(self.marketplace.uid, ObjectId(str(self.marketplace.id)))
        shouldContinue = True
        for report in reports:
            if shouldContinue and not report.filepath:
                try:
                    processedReport, shouldContinue = await self.__processAdExport(report)
                    if processedReport.res and processedReport.res.url: 
                        key = f'adexport/{report.exportType.value}/{processedReport.res.exportId}'
                        dataStr, processedReport.filepath = reportUtil.insertToS3(key, processedReport.res.url, False)
                        await self.__convertExportReport(report.exportType, dataStr)
                except APIError as e:
                    processedReport.error = e.error_list
                if report.model_dump() != processedReport.model_dump():
                    await db.updateChildReport(processedReport.id, processedReport.model_dump(exclude_none=True, exclude_defaults=True))

    def __convertExportFileToList(self, dataStr: str)->list[dict]:
        data: list[dict] = []
        for line in json.loads(dataStr):
            lineAsDict = json.loads(line)
            data.append(lineAsDict)
        return data

    async def __convertExportReport(self, exportType: AdExportType, dataStr: str):
        from amazon_daily_report.reports.report_types.adexport.AdsExportConvertor import AdsExportConvertor
        data = self.__convertExportFileToList(dataStr)
        exports = AdsExportConvertor().getExportData(exportType, data, str(self.marketplace.id))
        await self.reportUtil.update(self.dbClient, CollectionType.ADV_ASSETS, exports, self.reportId)
