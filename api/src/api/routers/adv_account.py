from dzgroshared.models.collections.advertising_accounts import AdAccount, AdAccountsList, AdvertisingAccount, AdvertisingAccountRequest, AdvertisingAccountUrlResponse, AdvertisingAccountList
from dzgroshared.models.collections.country_details import CountriesByRegionList
from dzgroshared.models.collections.user import TempAccountRequest
from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.models.model import Paginator, PyObjectId, RenameAccountRequest, SuccessResponse
router = APIRouter(prefix="/advertising-account", tags=["Advertising Account"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.advertising_accounts


@router.post("/list", response_model=AdvertisingAccountList, response_model_exclude_none=True, response_model_by_alias=False)
async def getAdvertisingAccounts(request: Request, paginator: Paginator):
    return await (await db(request)).getAdvertisingAccounts(paginator)

@router.put("/rename", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def renameAdvertisingAccount(request: Request, body: RenameAccountRequest):
    return await (await db(request)).rename(body)

@router.get("/countries", response_model=CountriesByRegionList, response_model_exclude_none=True)
async def getSupportedCountries(request: Request):
    return await (await RequestHelper(request).client).db.country_details.getCountriesByRegion()

@router.post("/new", response_model=AdvertisingAccountUrlResponse, response_model_exclude_none=True)
async def getUrl(request: Request, req: TempAccountRequest):
    return await (await db(request)).getUrl(req)

@router.post("/authorise", response_model=AdvertisingAccount, response_model_exclude_none=True)
async def authoriseSeller(request: Request, data: AdvertisingAccountRequest):
    return await (await db(request)).authoriseAccount(data)

@router.get("/adaccounts/{id}", response_model=AdAccountsList)
async def getAdAccounts(request: Request, id: PyObjectId):
    return await (await db(request)).getAdAccounts(id)


