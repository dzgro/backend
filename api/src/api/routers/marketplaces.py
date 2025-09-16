from calendar import Month
from dzgroshared.db.enums import PlanType
from dzgroshared.db.marketplaces.model import MarketplaceOnboardPaymentRequest, UserMarketplaceList
from dzgroshared.db.pricing.model import Pricing, PricingDetail
from dzgroshared.db.model import AddMarketplaceRequest, Paginator, PeriodDataRequest, PeriodDataResponse, PyObjectId, SuccessResponse
from dzgroshared.razorpay.common import RazorpayOrderObject
from fastapi import APIRouter, Request
from api.Util import RequestHelper
router = APIRouter(prefix="/marketplaces", tags=["Marketplaces"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.marketplaces

@router.get('/months/list', response_model=list[Month], response_model_exclude_none=True, response_model_by_alias=False)
async def listMonths(request: Request):
    return await (await db(request)).getMonths()

@router.post("/list", response_model=UserMarketplaceList, response_model_exclude_none=True, response_model_by_alias=False)
async def getUserMarketplaces(request: Request, paginator: Paginator):
    return await (await db(request)).getMarketplaces(paginator)

@router.post("/test/linkage", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def testLinkage(request: Request, req: AddMarketplaceRequest):
    return await (await db(request)).testLinkage(req)

@router.post("/add", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def addNewMarketplace(request: Request, req: AddMarketplaceRequest):
    return await (await db(request)).addMarketplace(req)

@router.get("/{id}/pricing", response_model=PricingDetail, response_model_exclude_none=True, response_model_by_alias=False)
async def getMarketplacePricing(request: Request, id: PyObjectId):
    return await (await db(request)).getPlanDetails(id)

@router.get("/{id}/plans", response_model=Pricing, response_model_exclude_none=True, response_model_by_alias=False)
async def getPlans(request: Request, id: PyObjectId):
    return await (await db(request)).getPlans(id)

@router.post("/onboard", response_model=RazorpayOrderObject, response_model_exclude_none=True, response_model_by_alias=False)
async def getPaymentObject(request: Request, req: MarketplaceOnboardPaymentRequest):
    return await (await db(request)).generateOrderForOnboarding(req)

@router.post("/{id}/period-data", response_model=PeriodDataResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getPeriodData(request: Request, req: PeriodDataRequest):
    return await (await db(request)).getPeriodData(req)