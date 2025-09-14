from dzgroshared.db.performance_periods.model import PerformancePeriodList
from fastapi import APIRouter, Request
router = APIRouter(prefix="/performance/periods", tags=["Periods"])
from api.Util import RequestHelper


async def db(request: Request):
    return (await RequestHelper(request).client).db.performance_periods


@router.get("/periods", response_model=PerformancePeriodList, response_model_exclude_none=True, response_model_by_alias=False)
async def getPerformancePeriods(request: Request):
    return await (await db(request)).getPerformancePeriods()