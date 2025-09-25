from dzgroshared.db.date_analytics.model import ChartData, MonthDateTableResponse, MonthLiteResponse, MonthTableResponse
from dzgroshared.db.state_analytics.model import AllStateData, StateRequest, StateDetailedDataResponse, StateMonthDataResponse
from dzgroshared.db.model import MonthDataRequest, PeriodDataRequest, PeriodDataResponse, SingleMetricPeriodDataRequest
from fastapi import APIRouter, Request
from api.Util import RequestHelper
router = APIRouter(prefix="/analytics/dates", tags=["Date Analytics"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.date_analytics

@router.post("/months/all", response_model=MonthTableResponse, response_model_exclude_none=True)
async def getMonthlyDataTable(request: Request, req: PeriodDataRequest):
    return await (await db(request)).getMonthlyDataTable(req)


@router.post("/months/lite", response_model=MonthLiteResponse, response_model_exclude_none=True)
async def getMonthLiteData(request: Request, req: PeriodDataRequest):
    return await (await db(request)).getMonthLiteData(req)

@router.post("/months", response_model=MonthDateTableResponse, response_model_exclude_none=True)
async def getMonthDateDataTable(request: Request, req: MonthDataRequest):
    return await (await db(request)).getMonthDatesDataTable(req)


@router.post("/period", response_model=PeriodDataResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getPeriodData(request: Request, req: PeriodDataRequest):
    return await (await db(request)).getPeriodData(req)
