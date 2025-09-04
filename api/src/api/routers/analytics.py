from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.models.extras.ad_structure import StructureScoreResponse
from dzgroshared.models.collections.health import AmazonHealthReportConverted
from dzgroshared.models.collections.analytics import CollateTypeAndValue, MonthData, MonthWithDates, MonthlyCarousel, StateData
from dzgroshared.models.model import AnalyticKeyGroup, AnalyticsPeriodData, ChartData, Count 
from dzgroshared.models.collections.queries import Query, QueryList
from dzgroshared.models.collections.query_results import QueryRequest, QueryResult, QueryResultGroup, QueryTableResult
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/health", response_model=AmazonHealthReportConverted, response_model_exclude_none=True)
async def getHealth(request: Request):
    return await RequestHelper(request).client.db.health.getHealth()

@router.get("/ad-health", response_model=StructureScoreResponse, response_model_exclude_none=True)
async def getAdStructureHealth(request: Request):
    return await RequestHelper(request).client.db.ad_structure.getAdvertismentStructureScore()

@router.post("/periods", response_model=list[AnalyticsPeriodData], response_model_exclude_none=True)
async def getPeriodData(request: Request, req: CollateTypeAndValue):
    return await RequestHelper(request).client.db.analytics.getPeriodData(req)

@router.post("/chart/{key}", response_model=list[ChartData], response_model_exclude_none=True)
async def getChart(request: Request,key:str, req: CollateTypeAndValue):
    return await RequestHelper(request).client.db.analytics.getChartData(key, req)

@router.post("/query-table/{key}", response_model=list[QueryTableResult], response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryTable(request: Request, key:str, req: CollateTypeAndValue):
    return await RequestHelper(request).client.db.query_results.getQueryTable(key, req)

@router.get('/months/list', response_model=list[MonthWithDates], response_model_exclude_none=True, response_model_by_alias=False)
async def listMonths(request: Request):
    return await RequestHelper(request).client.db.analytics.getMonths()

@router.post("/months", response_model=list[MonthData], response_model_exclude_none=True)
async def getMonthsData(request: Request, req: CollateTypeAndValue):
    return await RequestHelper(request).client.db.analytics.getMonthlyDataTable(req)

@router.post("/months/{month}", response_model=MonthlyCarousel, response_model_exclude_none=True)
async def getMonthCarousel(request: Request, month: str, req: CollateTypeAndValue):
    return await RequestHelper(request).client.db.analytics.getMonthlyCarousel(req, month)

@router.post("/states/{month}", response_model=list[StateData], response_model_exclude_none=True)
async def getStateDataByMonth(request: Request, month:str, req: CollateTypeAndValue):
    return await RequestHelper(request).client.db.analytics.getStateDataByMonth(req, month)

@router.get('/keys', response_model=list[AnalyticKeyGroup], response_model_exclude_none=True, response_model_by_alias=False)
async def getAnalyticKeyGroups(request: Request):
    return await RequestHelper(request).client.db.calculation_keys.getGroups()

@router.get("/queries", response_model=QueryList, response_model_exclude_none=True, response_model_by_alias=False)
async def listQueries(request: Request):
    return await RequestHelper(request).client.db.queries.getQueries()

@router.post("/query-performance/{queryId}", response_model=list[QueryResultGroup], response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryPerformance(request: Request, queryId:str, req: CollateTypeAndValue):
    return await RequestHelper(request).client.db.query_results.getPerformanceByQuery(queryId, req)

@router.post("/queries", response_model=list[QueryResult], response_model_exclude_none=True, response_model_by_alias=False)
async def getPerformance(request: Request, body: QueryRequest):
    return await RequestHelper(request).client.db.query_results.getPerformance(body)

@router.post("/queries/count", response_model=Count, response_model_exclude_none=True, response_model_by_alias=False)
async def getQueryCount(request: Request, body: QueryRequest):
    return await RequestHelper(request).client.db.query_results.getCount(body)

