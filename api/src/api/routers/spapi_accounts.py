from dzgroshared.db.country_details.model import CountriesByRegionList
from dzgroshared.db.spapi_accounts.model import MarketplaceParticipations, SPAPIAccount, SPAPIAccountList, SPAPIAccountRequest, SPAPIAccountUrlResponse
from dzgroshared.db.users.model import TempAccountRequest
from dzgroshared.db.enums import CountryCode
from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.db.model import Count, Paginator, PyObjectId, RenameAccountRequest, SuccessResponse
router = APIRouter(prefix="/selling-account", tags=["Selling Partner Account"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.spapi_accounts

@router.post("/", response_model=SPAPIAccountList, response_model_exclude_none=True, response_model_by_alias=False)
async def getSellerAccounts(request: Request, paginator: Paginator):
    return await (await db(request)).getSellerAccounts(paginator)

@router.get("/count", response_model=Count, response_model_exclude_none=True, response_model_by_alias=False)
async def getSellerAccountsCount(request: Request):
    return await (await db(request)).getSellerAccountsCount()

@router.put("/", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def renameSPAPIAccount(request: Request, body: RenameAccountRequest):
    return await (await db(request)).rename(body)

@router.get("/countries", response_model=CountriesByRegionList, response_model_exclude_none=True)
async def getSupportedCountries(request: Request):
    return await (await RequestHelper(request).client).db.country_details.getCountriesByRegion()

@router.post("/new", response_model=SPAPIAccountUrlResponse, response_model_exclude_none=True)
async def getNewSellerAccountUrl(request: Request, req: TempAccountRequest):
    return await (await db(request)).getUrl(req)

@router.post("/authorise", response_model=SPAPIAccount, response_model_exclude_none=True)
async def authoriseSeller(request: Request, data: SPAPIAccountRequest):
    return await (await db(request)).authoriseSeller(data)

@router.get("/participations/{id}", response_model=MarketplaceParticipations)
async def getMarketplaces(request: Request, id: PyObjectId):
    return await (await db(request)).getMarketplaceParticipations(id)


