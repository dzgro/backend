from dzgroshared.db.date_analytics.model import ChartData, MonthDataResponse, MonthDateTableResponse, MonthTableResponse
from dzgroshared.db.state_analytics.model import AllStateData, StateDetailedDataByStateRequest, StateDetailedDataResponse, StateMonthDataResponse
from dzgroshared.db.model import MonthDataRequest, PeriodDataRequest, SingleMetricPeriodDataRequest
from fastapi import APIRouter, Request
from api.Util import RequestHelper
router = APIRouter(prefix="/months", tags=["Date Analytics"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.date_analytics

@router.post("/all", response_model=MonthTableResponse, response_model_exclude_none=True)
async def getMonthlyDataTable(request: Request, req: PeriodDataRequest):
    return await (await db(request)).getMonthlyDataTable(req)

@router.post("/dates", response_model=MonthDateTableResponse, response_model_exclude_none=True)
async def getMonthDateDataTable(request: Request, req: MonthDataRequest):
    return await (await db(request)).getMonthDatesDataTable(req)

@router.post("/lite", response_model=MonthDataResponse, response_model_exclude_none=True)
async def getMonthLiteData(request: Request, req: MonthDataRequest):
    return await (await db(request)).getMonthLiteData(req)


@router.post("/chart", response_model=list[ChartData], response_model_exclude_none=True)
async def getChart(request: Request,req: SingleMetricPeriodDataRequest):
    return await (await db(request)).getChartData(req)
