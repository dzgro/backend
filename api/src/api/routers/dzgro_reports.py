from dzgroshared.db.enums import CollateType, DzgroReportType
from dzgroshared.db.model import Paginator, Url
from fastapi import APIRouter, Query, Request
from dzgroshared.db.dzgro_reports.model import  DzgroReport, CreateDzgroReportRequest, ListDzgroReportsResponse
from dzgroshared.db.dzgro_report_types.model import DzgroReportSpecification
router = APIRouter(prefix="/report", tags=["Reports"])
from api.Util import RequestHelper
from pydantic.json_schema import SkipJsonSchema


async def db(request: Request):
    return (await RequestHelper(request).client).db.dzgro_reports

@router.post("/list", response_model=ListDzgroReportsResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def listReportsWithCount(request: Request, paginator: Paginator):
    return await (await db(request)).listReports(paginator)

@router.post("/create", response_model=DzgroReport, response_model_exclude_none=True, response_model_by_alias=False)
async def createReport(request: Request, body: CreateDzgroReportRequest):
    client = RequestHelper(request).client
    report = await (await db(request)).createReport(body)
    return report

@router.get("/fetch/{id}", response_model=DzgroReport, response_model_exclude_none=True, response_model_by_alias=False)
async def getReport(request: Request, id: str):
    return await (await db(request)).getReport(id)
    

@router.put("/link/{reportid}", response_model=Url, response_model_exclude_none=True)
async def createReportLink(request: Request, reportid: str):
    url = await (await db(request)).getDownloadUrl(reportid)
    return Url(url=url)


@router.get("/types", response_model=list[DzgroReportSpecification], response_model_exclude_none=True, response_model_by_alias=False)
async def getReportTypes(request: Request):
    return (await db(request)).dzgro_report_types.getReportTypes()

@router.get("/headers/{reporttype}", response_model=list[str], response_model_exclude_none=True, response_model_by_alias=False)
async def getReportHeaders(request: Request, reporttype: DzgroReportType, collatetype: CollateType|SkipJsonSchema[None]=Query(None)):
    return (await db(request)).dzgro_report_types.getSampleReportHeaders(reporttype, collatetype)

