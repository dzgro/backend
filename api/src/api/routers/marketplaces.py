from dzgroshared.db.marketplaces.model import MarketplacePlan, UserMarketplace, UserMarketplaceList
from dzgroshared.db.pricing.model import Pricing
from dzgroshared.db.model import AddMarketplaceRequest, Count, Month, Paginator, PeriodDataRequest, PeriodDataResponse, PyObjectId, SuccessResponse
from dzgroshared.razorpay.common import RazorpayOrderObject
from fastapi import APIRouter, Request
from api.Util import RequestHelper
router = APIRouter(prefix="/marketplaces", tags=["Marketplaces"])

async def db(request: Request):
    helper = RequestHelper(request)
    client = await helper.client
    db = client.db
    return db.marketplaces

@router.get('/months/list', response_model=list[Month], response_model_exclude_none=True, response_model_by_alias=False)
async def listMonths(request: Request):
    return await (await db(request)).getMonths()

@router.post("/", response_model=UserMarketplaceList, response_model_exclude_none=True, response_model_by_alias=False)
async def getUserMarketplaces(request: Request, paginator: Paginator):
    return await (await db(request)).getMarketplaces(paginator)

@router.get("/count", response_model=Count, response_model_exclude_none=True, response_model_by_alias=False)
async def getUserMarketplacesCount(request: Request):
    return await (await db(request)).getMarketplacesCount()

@router.get("/{id}", response_model=UserMarketplace, response_model_exclude_none=True, response_model_by_alias=False)
async def getUserMarketplace(request: Request, id: PyObjectId):
    return await (await db(request)).getUserMarketplace(id)

@router.post("/test/linkage", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def testLinkage(request: Request, req: AddMarketplaceRequest):
    return await (await db(request)).testLinkage(req)

@router.post("/add", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def addNewMarketplace(request: Request, req: AddMarketplaceRequest):
    return await (await db(request)).addMarketplace(req)

