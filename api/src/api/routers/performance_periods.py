from api.decorators import cache_control, enforce_response_model
from dzgroshared.db.model import PeriodDataRequest
from dzgroshared.db.performance_period_results.model import PerformanceDashboardResponse, PerformanceTableLiteResponse
from dzgroshared.db.performance_periods.model import PerformancePeriodList
from fastapi import APIRouter, Request
router = APIRouter(prefix="/performance/periods", tags=["Periods"])
from api.Util import RequestHelper


async def db(request: Request):
    return (await RequestHelper(request).client).db.performance_periods


@router.post("/dashboard", response_model=PerformanceDashboardResponse, response_model_exclude_none=True, response_model_by_alias=False)
@cache_control()
@enforce_response_model(PerformanceDashboardResponse)
async def getDashboardPerformanceResults(request: Request, req: PeriodDataRequest):
    return await (await db(request)).getDashboardPerformanceResults(req)


@router.post("/table/lite", response_model=PerformanceTableLiteResponse, response_model_exclude_none=True, response_model_by_alias=False)
@cache_control()
async def getPerformanceTableLite(request: Request, body: PeriodDataRequest):
    return await (await db(request)).getPerformanceTableLite(body)

@router.get("/periods", response_model=PerformancePeriodList, response_model_exclude_none=True, response_model_by_alias=False)
async def getPerformancePeriods(request: Request):
    return await (await db(request)).getPerformancePeriods()