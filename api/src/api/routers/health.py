from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.db.adv.adv_structure_rules.model import StructureScoreResponse
from dzgroshared.db.health.model import MarketplaceHealthResponse
router = APIRouter(prefix="/analytics", tags=["Analytics"])

async def db(request: Request):
    return (await RequestHelper(request).client).db

@router.get("/health/seller", response_model=MarketplaceHealthResponse, response_model_exclude_none=True)
async def getHealth(request: Request):
    return await (await db(request)).health.getHealth()

@router.get("/health/ad", response_model=StructureScoreResponse, response_model_exclude_none=True)
async def getAdStructureHealth(request: Request):
    return await (await db(request)).ad_structure.getAdvertismentStructureScore()

