from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.models.extras.ad_structure import StructureScoreResponse
from dzgroshared.models.collections.analytics import AllStateData, MarketplaceHealthResponse, MonthDataRequest, MonthDateTableResponse, MonthTableResponse, PeriodDataRequest, Month, MonthDataResponse, SingleAnalyticsMetricTableResponseItem, SingleMetricPeriodDataRequest, ComparisonPeriodDataRequest, PeriodDataResponse, ChartData, StateDetailedDataByStateRequest, StateDetailedDataResponse, StateMonthDataResponse, PerformancePeriodDataResponse
from dzgroshared.models.collections.query_results import PerformanceTableRequest, PerformanceTableResponse
from dzgroshared.models.model import AnalyticKeyGroup, Count 
from dzgroshared.models.collections.queries import QueryList
router = APIRouter(prefix="/analytics", tags=["Analytics"])

async def db(request: Request):
    return (await RequestHelper(request).client).db

@router.get("/health/seller", response_model=MarketplaceHealthResponse, response_model_exclude_none=True)
async def getHealth(request: Request):
    return await (await db(request)).health.getHealth()

@router.get("/health/ad", response_model=StructureScoreResponse, response_model_exclude_none=True)
async def getAdStructureHealth(request: Request):
    return await (await db(request)).ad_structure.getAdvertismentStructureScore()

@router.post("/periods", response_model=PeriodDataResponse, response_model_exclude_none=True)
async def getPeriodData(request: Request, req: PeriodDataRequest):
    return await (await db(request)).analytics.getPeriodData(req)

@router.post("/chart", response_model=list[ChartData], response_model_exclude_none=True)
async def getChart(request: Request,req: SingleMetricPeriodDataRequest):
    return await (await db(request)).analytics.getChartData(req)

@router.post("/performance/table", response_model=list[SingleAnalyticsMetricTableResponseItem], response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryTable(request: Request, req: SingleMetricPeriodDataRequest):
    return await (await db(request)).queries.getQueryTable(req)

@router.get('/months/list', response_model=list[Month], response_model_exclude_none=True, response_model_by_alias=False)
async def listMonths(request: Request):
    return await (await db(request)).analytics.getMonths()

@router.post("/months/all", response_model=MonthTableResponse, response_model_exclude_none=True)
async def getMonthlyDataTable(request: Request, req: PeriodDataRequest):
    return await (await db(request)).analytics.getMonthlyDataTable(req)

@router.post("/months/dates", response_model=MonthDateTableResponse, response_model_exclude_none=True)
async def getMonthDateDataTable(request: Request, req: MonthDataRequest):
    return await (await db(request)).analytics.getMonthDatesDataTable(req)

@router.post("/months/lite", response_model=MonthDataResponse, response_model_exclude_none=True)
async def getMonthLiteData(request: Request, req: MonthDataRequest):
    return await (await db(request)).analytics.getMonthLiteData(req)

@router.post("/states/detailed/month", response_model=AllStateData, response_model_exclude_none=True)
async def getStateDataDetailedForMonth(request: Request, req: MonthDataRequest):
    return await (await db(request)).analytics.getStateDataDetailedForMonth(req)

@router.post("/states/detailed", response_model=StateDetailedDataResponse, response_model_exclude_none=True)
async def getStateDataDetailed(request: Request, req: StateDetailedDataByStateRequest):
    return await (await db(request)).analytics.getStateDataDetailed(req)

@router.post("/states/lite", response_model=StateMonthDataResponse, response_model_exclude_none=True)
async def getStateDataLiteByMonth(request: Request, req: MonthDataRequest):
    return await (await db(request)).analytics.getStateDataLiteByMonth(req)

@router.get('/keys', response_model=list[AnalyticKeyGroup], response_model_exclude_none=True, response_model_by_alias=False)
async def getAnalyticKeyGroups(request: Request):
    await db(request)
    from dzgroshared.db.extras import Analytics
    return Analytics.getAnalyticsGroups()

@router.get("/queries", response_model=QueryList, response_model_exclude_none=True, response_model_by_alias=False)
async def listQueries(request: Request):
    return await (await db(request)).queries.getQueries()

@router.post("/query/performance", response_model=PerformancePeriodDataResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryPerformance(request: Request, req: ComparisonPeriodDataRequest):
    return await (await db(request)).query_results.getPerformanceforPeriod(req)

@router.post("/queries", response_model=PerformanceTableResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getPerformanceTable(request: Request, body: PerformanceTableRequest):
    return await (await db(request)).query_results.getPerformanceListforPeriod(body)

@router.post("/queries/count", response_model=Count, response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryCount(request: Request, body: PerformanceTableRequest):
    return {"count": await (await db(request)).query_results.getCount(body)}

