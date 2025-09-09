from dzgroshared.models.enums import CollateType, DzgroReportType
from dzgroshared.models.model import Paginator, Url
from fastapi import APIRouter, Query, Request
from dzgroshared.models.collections.dzgro_reports import  DzgroReport, CreateDzgroReportRequest, ListDzgroReportsResponse
from dzgroshared.models.collections.dzgro_report_types import DzgroReportSpecification
router = APIRouter(prefix="/report", tags=["Reports"])
from api.Util import RequestHelper
from pydantic.json_schema import SkipJsonSchema


async def db(request: Request):
    return (await RequestHelper(request).client).db

@router.post("/list", response_model=ListDzgroReportsResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def listReportsWithCount(request: Request, paginator: Paginator):
    return (await db(request)).dzgro_reports.listReports(paginator)

@router.post("/create", response_model=DzgroReport, response_model_exclude_none=True, response_model_by_alias=False)
async def createReport(request: Request, body: CreateDzgroReportRequest):
    client = RequestHelper(request).client
    report = await (await db(request)).dzgro_reports.createReport(body)
    return report

@router.get("/fetch/{id}", response_model=DzgroReport, response_model_exclude_none=True, response_model_by_alias=False)
async def getReport(request: Request, id: str):
    client = RequestHelper(request).client
    utility = (await db(request)).dzgro_reports
    report = await utility.getReport(id)
    return report

@router.put("/link/{reportid}", response_model=Url, response_model_exclude_none=True)
async def createReportLink(request: Request, reportid: str):
    client = RequestHelper(request).client
    utility = (await db(request)).dzgro_reports
    url = await utility.getDownloadUrl(reportid)
    return Url(url=url)


@router.get("/types", response_model=list[DzgroReportSpecification], response_model_exclude_none=True, response_model_by_alias=False)
async def getReportTypes(request: Request):
    return (await db(request)).dzgro_report_types.getReportTypes()

@router.get("/headers/{reporttype}", response_model=list[str], response_model_exclude_none=True, response_model_by_alias=False)
async def getReportHeaders(request: Request, reporttype: DzgroReportType, collatetype: CollateType|SkipJsonSchema[None]=Query(None)):
    return (await db(request)).dzgro_report_types.getSampleReportHeaders(reporttype, collatetype)

