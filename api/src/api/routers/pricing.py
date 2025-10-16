from dzgroshared.db.model import MarketplacePlanOrderObject, MarketplacePlan, PyObjectId
from dzgroshared.db.pricing.model import MarketplacePricing, Pricing
from dzgroshared.razorpay.common import RazorpayOrderObject
from fastapi import APIRouter, Request
from api.Util import RequestHelper
router = APIRouter(prefix="/pricing", tags=["Pricing"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.pricing


@router.get("/", response_model=Pricing, response_model_exclude_none=True, response_model_by_alias=False)
async def getPricing(request: Request):
    return await (await db(request)).getPricing()

@router.get("/marketplace/{id}", response_model=MarketplacePricing, response_model_exclude_none=True, response_model_by_alias=False)
async def getMarketplacePricing(request: Request, id: PyObjectId):
    return await (await db(request)).getMarketplacePricing(id)

@router.post("/marketplace/order", response_model=RazorpayOrderObject, response_model_exclude_none=True, response_model_by_alias=False)
async def generateOrderForMarketplace(request: Request, req: MarketplacePlanOrderObject):
    return await (await db(request)).generateOrderForMarketplace(req)