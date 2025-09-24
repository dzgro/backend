from dzgroshared.db.performance_period_results.model import ComparisonPeriodDataRequest, PerformanceDashboardResponse, PerformanceTableRequest, PerformanceTableResponse
from dzgroshared.db.model import Count, PeriodDataRequest, SingleAnalyticsMetricTableResponse, SingleMetricPeriodDataRequest
from fastapi import APIRouter, Request
router = APIRouter(prefix="/performance/results", tags=["Performance Results"])
from api.Util import RequestHelper


async def db(request: Request):
    return (await RequestHelper(request).client).db.performance_period_results


@router.post("", response_model=PerformanceDashboardResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getDashboardPerformanceResults(request: Request, req: PeriodDataRequest):
    return await (await db(request)).getDashboardPerformanceResults(req)

@router.post("/table", response_model=PerformanceTableResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getPerformanceListforPeriod(request: Request, body: PerformanceTableRequest):
    return await (await db(request)).getPerformanceListforPeriod(body)

@router.post("/metric", response_model=SingleAnalyticsMetricTableResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getPerformanceTable(request: Request, body: SingleMetricPeriodDataRequest):
    return await (await db(request)).getPerformanceTable(body)

@router.post("/table/count", response_model=Count, response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryCount(request: Request, body: PerformanceTableRequest):
    return {"count": await (await db(request)).getCount(body)}

