from fastapi import APIRouter, Request, Query, Body,Path,Depends
from pydantic.json_schema import SkipJsonSchema
router = APIRouter(prefix="/pricing", tags=["Pricing"])
from dzgroshared.models.collections.pricing import Pricing
from api.Util import RequestHelper

@router.get("/plans", response_model=Pricing, response_model_exclude_none=True, response_model_by_alias=False)
async def getPlans(request: Request):
    return await RequestHelper(request).client.db.pricing.getPlans()