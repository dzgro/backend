from fastapi import APIRouter, Request, Query
from dzgroshared.db.extras.Onboarding import OnboardingHelper
from api.Util import RequestHelper
from dzgroshared.models.collections.pricing import PricingDetail
from dzgroshared.models.collections.country_details import CountriesByRegion
from dzgroshared.models.collections.spapi_accounts import SPAPIAccountRequest
from dzgroshared.models.collections.advertising_accounts import AdvertisingAccountRequest
from dzgroshared.models.enums import AmazonAccountType
from dzgroshared.models.model import SuccessResponse, AdAccount, AddMarketplace
from dzgroshared.models.razorpay.common import RazorpaySubscriptionObject
from dzgroshared.models.collections.subscriptions import CreateSubscriptionRequest
from dzgroshared.models.amazonapi.spapi.sellers import MarketplaceItem
router = APIRouter(prefix='/onboarding', tags=["Onboarding"])


def getOnboardingManager(request: Request)->OnboardingHelper:
    return OnboardingHelper(RequestHelper(request).client)

@router.get("/pricing/{marketplaceid}", response_model=PricingDetail, response_model_exclude_none=True, response_model_by_alias=False)
async def getPricing(request: Request, marketplaceid:str, planid: str ):
    return await getOnboardingManager(request).getPlanDetails(marketplaceid, planid)

@router.get("/countries/{accountType}", response_model=list[CountriesByRegion], response_model_exclude_none=True)
async def get_supported_marketplaces(request: Request, accountType: AmazonAccountType):
    return await getOnboardingManager(request).getUrls(accountType)

@router.post("/authorise/seller", response_model=SuccessResponse, response_model_exclude_none=True)
async def authoriseSeller(request: Request, query: SPAPIAccountRequest):
    return await getOnboardingManager(request).addSeller(query)

@router.post("/authorise/advertising", response_model=SuccessResponse, response_model_exclude_none=True)
async def authoriseAdvertising(request: Request, query: AdvertisingAccountRequest):
    return await getOnboardingManager(request).addAdvertisingAccount(query)

@router.post("/subscription", response_model=RazorpaySubscriptionObject, response_model_exclude_none=True)
async def getSubscription(request: Request, body: CreateSubscriptionRequest):
    return await getOnboardingManager(request).getSubscription(body)

@router.post("/verify/subscription", response_model=SuccessResponse, response_model_exclude_none=True)
async def verifySubscription(request: Request, query: dict):
    return await getOnboardingManager(request).verifySubscription(query)

@router.get("/marketplaces/{id}", response_model=list[MarketplaceItem])
async def getMarketplaces(request: Request, id: str):
    return await getOnboardingManager(request).getMarketplaceParticipations(id)

@router.get("/adaccounts/{id}", response_model=list[AdAccount])
async def getAdAccounts(request: Request, id: str):
    return await getOnboardingManager(request).getAdAccounts(id)

@router.post("/marketplace", response_model=SuccessResponse)
async def addMarketplace(request: Request, req: AddMarketplace):
    manager = getOnboardingManager(request)
    return await manager.addMarketplace(req)

@router.post("/test-linkage", response_model=SuccessResponse)
async def testLinkage(request: Request, req: AddMarketplace):
    manager = getOnboardingManager(request)
    return await manager.testLinkage(req)

