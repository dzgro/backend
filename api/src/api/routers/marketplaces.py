from dzgroshared.models.collections.pricing import PricingDetail
from dzgroshared.models.razorpay.common import RazorpayOrderObject
from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.models.collections.marketplaces import MarketplaceOnboardPaymentRequest, UserMarketplaceList
from dzgroshared.models.model import AddMarketplaceRequest, Paginator, PyObjectId, SuccessResponse
router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.marketplaces

@router.post("/list", response_model=UserMarketplaceList, response_model_exclude_none=True, response_model_by_alias=False)
async def getUserMarketplaces(request: Request, paginator: Paginator):
    return await (await db(request)).getMarketplaces(paginator)

@router.post("/test/linkage", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def testLinkage(request: Request, req: AddMarketplaceRequest):
    return await (await db(request)).testLinkage(req)

@router.post("/add", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def addNewMarketplace(request: Request, req: AddMarketplaceRequest):
    return await (await db(request)).addMarketplace(req)

@router.get("/pricing/{id}/{planid}", response_model=PricingDetail, response_model_exclude_none=True, response_model_by_alias=False)
async def getMarketplacePricing(request: Request, id: PyObjectId, planid: str):
    return await (await db(request)).getPlanDetails(id, planid)

@router.post("/onboard/{id}", response_model=RazorpayOrderObject, response_model_exclude_none=True, response_model_by_alias=False)
async def getPaymentObject(request: Request, req: MarketplaceOnboardPaymentRequest):
    return await (await db(request)).generateOrderForOnboarding(req)