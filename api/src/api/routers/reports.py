from dzgroshared.models.enums import DzgroReportType
from dzgroshared.models.model import Paginator, Url
from fastapi import APIRouter, Request
from dzgroshared.models.collections.dzgro_reports import  DzgroReport, CreateDzgroReportRequest
from dzgroshared.models.collections.dzgro_report_types import DzgroReportSpecification
router = APIRouter(prefix="/reports", tags=["Reports"])
from api.Util import RequestHelper

@router.post("/report", response_model=DzgroReport, response_model_exclude_none=True, response_model_by_alias=False)
async def createReport(request: Request, body: CreateDzgroReportRequest):
    client = RequestHelper(request).client
    utility = client.db.dzgro_reports
    report = await utility.createReport(body)
    return report

@router.put("/reportlink/{reportid}", response_model=Url, response_model_exclude_none=True)
async def createReportLink(request: Request, reportid: str):
    client = RequestHelper(request).client
    utility = client.db.dzgro_reports
    url = await utility.getDownloadUrl(reportid)
    return Url(url=url)

@router.post("/reports", response_model=list[DzgroReport], response_model_exclude_none=True, response_model_by_alias=False)
async def listReports(request: Request, body: Paginator):
    return await RequestHelper(request).client.db.dzgro_reports.listReports(body)

@router.get("/report-types", response_model=list[DzgroReportSpecification], response_model_exclude_none=True, response_model_by_alias=False)
async def getReportTypes(request: Request):
    return await RequestHelper(request).client.db.dzgro_report_types.getReportTypes()

@router.get("/report-headers/{reporttype}", response_model=list[str], response_model_exclude_none=True, response_model_by_alias=False)
async def getReportHeaders(request: Request, reporttype: DzgroReportType):
    return await RequestHelper(request).client.db.dzgro_report_types.getSampleReportHeaders(reporttype)

