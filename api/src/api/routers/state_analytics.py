from dzgroshared.db.state_analytics.model import AllStateData, StateRequest, StateDetailedDataResponse, StateMonthDataResponse
from dzgroshared.db.model import MonthDataRequest
from fastapi import APIRouter, Request
from api.Util import RequestHelper
router = APIRouter(prefix="/states", tags=["State Analytics"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.state_analytics

@router.post("/detailed/month", response_model=AllStateData, response_model_exclude_none=True)
async def getStateDataDetailedForMonth(request: Request, req: MonthDataRequest):
    return await (await db(request)).getStateDataDetailedForMonth(req)

@router.post("/detailed", response_model=StateDetailedDataResponse, response_model_exclude_none=True)
async def getStateDataDetailed(request: Request, req: StateRequest):
    return await (await db(request)).getStateDataDetailed(req)

@router.post("/lite", response_model=StateMonthDataResponse, response_model_exclude_none=True)
async def getStateDataLiteByMonth(request: Request, req: MonthDataRequest):
    return await (await db(request)).getStateDataLiteByMonth(req)

