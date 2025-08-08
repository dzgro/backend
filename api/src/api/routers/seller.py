from fastapi import APIRouter, Depends, Request, Query,Path
router = APIRouter(prefix='/seller', tags=["seller"])
from models.model import Paginator, SuccessResponse
from models.collections.spapi_accounts import SPAPIAccountRequest, RenameSPAPIAccount
from models.collections.advertising_accounts import AdvertisingAccountRequest, RenameAdvertisingAccount
from api.Util import RequestHelper

@router.post("/rename/spapi", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def renameSPAPIAccount(request: Request, body: RenameSPAPIAccount):
    return await RequestHelper(request).spapi_accounts.rename(body)

@router.post("/rename/advertising", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def renameAdvertisingAccount(request: Request, body: RenameAdvertisingAccount):
    return await RequestHelper(request).advertising_accounts.rename(body)
