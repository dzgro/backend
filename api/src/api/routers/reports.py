from fastapi import APIRouter, BackgroundTasks, Request, Body,Path
from dzgroshared.models.collections.dzgro_reports import AvailableDzgroReport, DzgroReport, CreateDzgroReportRequest, ListDzgroReportsRequest
router = APIRouter(prefix="/reports", tags=["Reports"])
from api.Util import RequestHelper

@router.post("/report", response_model=DzgroReport, response_model_exclude_none=True)
async def createReport(request: Request, body: CreateDzgroReportRequest):
    client = RequestHelper(request).client
    utility = client.db.dzgro_reports
    report = await utility.createReport(body)
    return report

@router.post("/reports", response_model=list[DzgroReport], response_model_exclude_none=True, response_model_by_alias=False)
async def listReports(request: Request, body: ListDzgroReportsRequest):
    return await RequestHelper(request).client.db.dzgro_reports.listReports(body)

@router.get("/report-types", response_model=list[AvailableDzgroReport], response_model_exclude_none=True, response_model_by_alias=False)
def getReportTypes(request: Request):
    return RequestHelper(request).client.db.dzgro_reports.getReportTypes()
