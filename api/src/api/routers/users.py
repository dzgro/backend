from fastapi import APIRouter, Request, Depends
from api.Util import RequestHelper
from dzgroshared.db.users.model import MarketplaceOnboarding
router = APIRouter(prefix="/user", tags=["User"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.users

@router.get("/onboarding", response_model=MarketplaceOnboarding, response_model_exclude_none=True, response_model_by_alias=False)
async def getMarketplaceOnboarding(request: Request):
    return await (await db(request)).getMarketplaceOnboarding()


# @router.get("/signout", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
# def signout(request: Request):
#     manager = getManager(request)
#     token = request.headers.get('token')
#     if token: manager.signout(token)
#     return SuccessResponse(success=True)

# @router.get("/image", response_model=SuccessResponse, response_model_exclude_none=True)
# async def uploadImage(request: Request, uid: str = Query(None)):
#     manager = getManager(request)
#     return await manager.getUploadImageLink(uid)
