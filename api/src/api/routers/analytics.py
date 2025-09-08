from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.models.extras.ad_structure import StructureScoreResponse
from dzgroshared.models.collections.health import AmazonHealthReportConverted
from dzgroshared.models.collections.analytics import AllStateData, MonthDataRequest, MonthDateTableResponse, MonthTableResponse, PeriodDataRequest, Month, MonthDataResponse, SingleAnalyticsMetricTableResponseItem, SingleMetricPeriodDataRequest, ComparisonPeriodDataRequest, PeriodDataResponse, ChartData, StateDetailedDataByStateRequest, StateDetailedDataResponse, StateMonthDataResponse, PerformancePeriodDataResponse
from dzgroshared.models.collections.query_results import QueryRequest, QueryResult
from dzgroshared.models.model import AnalyticKeyGroup, Count 
from dzgroshared.models.collections.queries import QueryList
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/health/seller", response_model=AmazonHealthReportConverted, response_model_exclude_none=True)
async def getHealth(request: Request):
    return await RequestHelper(request).client.db.health.getHealth()

@router.get("/health/ad", response_model=StructureScoreResponse, response_model_exclude_none=True)
async def getAdStructureHealth(request: Request):
    return await RequestHelper(request).client.db.ad_structure.getAdvertismentStructureScore()

@router.post("/periods", response_model=PeriodDataResponse, response_model_exclude_none=True)
async def getPeriodData(request: Request, req: PeriodDataRequest):
    return await RequestHelper(request).client.db.analytics.getPeriodData(req)

@router.post("/chart", response_model=list[ChartData], response_model_exclude_none=True)
async def getChart(request: Request,req: SingleMetricPeriodDataRequest):
    return await RequestHelper(request).client.db.analytics.getChartData(req)

@router.post("/performance/table", response_model=list[SingleAnalyticsMetricTableResponseItem], response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryTable(request: Request, req: SingleMetricPeriodDataRequest):
    return await RequestHelper(request).client.db.queries.getQueryTable(req)

@router.get('/months/list', response_model=list[Month], response_model_exclude_none=True, response_model_by_alias=False)
async def listMonths(request: Request):
    return await RequestHelper(request).client.db.analytics.getMonths()

@router.post("/months/all", response_model=MonthTableResponse, response_model_exclude_none=True)
async def getMonthlyDataTable(request: Request, req: PeriodDataRequest):
    return await RequestHelper(request).client.db.analytics.getMonthlyDataTable(req)

@router.post("/months/dates", response_model=MonthDateTableResponse, response_model_exclude_none=True)
async def getMonthDateDataTable(request: Request, req: MonthDataRequest):
    return await RequestHelper(request).client.db.analytics.getMonthDatesDataTable(req)

@router.post("/months/lite", response_model=MonthDataResponse, response_model_exclude_none=True)
async def getMonthLiteData(request: Request, req: MonthDataRequest):
    return await RequestHelper(request).client.db.analytics.getMonthLiteData(req)

@router.post("/states/detailed/month", response_model=AllStateData, response_model_exclude_none=True)
async def getStateDataDetailedForMonth(request: Request, req: MonthDataRequest):
    return await RequestHelper(request).client.db.analytics.getStateDataDetailedForMonth(req)

@router.post("/states/detailed", response_model=StateDetailedDataResponse, response_model_exclude_none=True)
async def getStateDataDetailed(request: Request, req: StateDetailedDataByStateRequest):
    return await RequestHelper(request).client.db.analytics.getStateDataDetailed(req)

@router.post("/states/lite", response_model=StateMonthDataResponse, response_model_exclude_none=True)
async def getStateDataLiteByMonth(request: Request, req: MonthDataRequest):
    return await RequestHelper(request).client.db.analytics.getStateDataLiteByMonth(req)

@router.get('/keys', response_model=list[AnalyticKeyGroup], response_model_exclude_none=True, response_model_by_alias=False)
async def getAnalyticKeyGroups(request: Request):
    RequestHelper(request)
    from dzgroshared.db.extras import Analytics
    return Analytics.getAnalyticsGroups()

@router.get("/queries", response_model=QueryList, response_model_exclude_none=True, response_model_by_alias=False)
async def listQueries(request: Request):
    return await RequestHelper(request).client.db.queries.getQueries()

@router.post("/query/performance", response_model=PerformancePeriodDataResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryPerformance(request: Request, req: ComparisonPeriodDataRequest):
    return await RequestHelper(request).client.db.query_results.getPerformanceforPeriod(req)

@router.post("/queries", response_model=list[QueryResult], response_model_exclude_none=True, response_model_by_alias=False)
async def getPerformance(request: Request, body: QueryRequest):
    return await RequestHelper(request).client.db.query_results.getPerformance(body)

@router.post("/queries/count", response_model=Count, response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryCount(request: Request, body: QueryRequest):
    return await RequestHelper(request).client.db.query_results.getCount(body)

