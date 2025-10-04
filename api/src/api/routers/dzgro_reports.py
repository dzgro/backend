from dzgroshared.db.enums import CollateType, DzgroReportType
from dzgroshared.db.model import Count, Paginator, Url
from fastapi import APIRouter, Query, Request
from dzgroshared.db.dzgro_reports.model import  DzgroReport, CreateDzgroReportRequest, ListDzgroReportsResponse
from dzgroshared.db.dzgro_report_types.model import AvailableReports, DzgroReportSpecification
router = APIRouter(prefix="/reports", tags=["Reports"])
from api.Util import RequestHelper
from pydantic.json_schema import SkipJsonSchema


async def db(request: Request):
    return (await RequestHelper(request).client).db

@router.post("/list", response_model=ListDzgroReportsResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def listReports(request: Request, paginator: Paginator):
    return await ((await db(request)).dzgro_reports.listReports(paginator))

@router.get("/count", response_model=Count, response_model_exclude_none=True, response_model_by_alias=False)
async def countReports(request: Request):
    return await ((await db(request)).dzgro_reports.count())

@router.post("", response_model=DzgroReport, response_model_exclude_none=True, response_model_by_alias=False)
async def createReport(request: Request, body: CreateDzgroReportRequest):
    report = await (await db(request)).dzgro_reports.createReport(body)
    return report


@router.put("/link/{id}", response_model=Url, response_model_exclude_none=True)
async def createReportLink(request: Request, id: str):
    url = await (await db(request)).dzgro_reports.getDownloadUrl(id)
    return Url(url=url)

@router.get("/types", response_model=AvailableReports, response_model_exclude_none=True, response_model_by_alias=False)
async def getReportTypes(request: Request):
    return await (await db(request)).dzgro_report_types.getReportTypes()

@router.get("/sample/{reporttype}", response_model=list[str], response_model_exclude_none=True, response_model_by_alias=False)
async def getReportHeaders(request: Request, reporttype: DzgroReportType, collatetype: CollateType|SkipJsonSchema[None]=Query(None)):
    return await (await db(request)).dzgro_report_types.getSampleReportHeaders(reporttype, collatetype)

@router.get("/{id}", response_model=DzgroReport, response_model_exclude_none=True, response_model_by_alias=False)
async def getReport(request: Request, id: str):
    return await (await db(request)).dzgro_reports.getReport(id)

