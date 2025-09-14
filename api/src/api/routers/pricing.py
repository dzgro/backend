from fastapi import APIRouter, Request, Query, Body,Path,Depends
from pydantic.json_schema import SkipJsonSchema
router = APIRouter(prefix="/pricing", tags=["Pricing"])
from dzgroshared.db.pricing.model import Pricing
from api.Util import RequestHelper


async def db(request: Request):
    return (await RequestHelper(request).client).db

@router.get("/plans", response_model=Pricing, response_model_exclude_none=True, response_model_by_alias=False)
async def getPlans(request: Request):
    return (await db(request)).pricing.getPlans()