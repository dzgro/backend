from fastapi import APIRouter, Request, Depends
from api.Util import RequestHelper
from dzgroshared.models.collections.marketplaces import Marketplace
from dzgroshared.models.collections.user import UserProfileWithSubscription, UserWithAccounts, BusinessDetails
from dzgroshared.models.model import SuccessResponse
router = APIRouter(prefix="/user", tags=["User"])

async def db(request: Request):
    return (await RequestHelper(request).client).db

@router.get("/marketplace/{marketplace}", response_model=Marketplace, response_model_exclude_none=True, response_model_by_alias=False)
async def getActiveAMarketplace(request: Request, marketplace: str):
    return await (await db(request)).marketplaces.getMarketplace(marketplace)

@router.get("/subscription", response_model=UserProfileWithSubscription, response_model_exclude_none=True, response_model_by_alias=False)
async def getUserSubscriptionWithPlan(request: Request):
    return await (await db(request)).user.getUserBusinessWithActivePlanAndSubscriptionStatus()

@router.get("/accounts", response_model=UserWithAccounts, response_model_exclude_none=True, response_model_by_alias=False)
async def getUserAccounts(request: Request):
    req = RequestHelper(request)
    _user = (await req.client).db.user
    try: return await _user.getUserAccounts()
    except Exception as e:
        if e.args[0] == "Not Found":
            from dzgroshared.cognito.client import CognitoManager
            uid, details = await CognitoManager(req.secrets.COGNITO_APP_CLIENT_ID, req.secrets.COGNITO_USER_POOL_ID).get_user(req.uid)
            await _user.addUserToDb(details)
            return await _user.getUserAccounts()
        raise e

@router.post("/business-details", response_model=SuccessResponse)
async def updateBusinessDetails(request: Request, details: BusinessDetails):
    return await (await db(request)).user.updateBusinessDetails(details)

# @router.post("/payments", response_model=Payments, response_model_exclude_none=True, response_model_by_alias=False)
# async def getPayments(request: Request, paginator: Paginator):
#     manager = getManager(request)
#     return await manager.getPayments(paginator)

# @router.get("/payment-link/{id}", response_model=Payment, response_model_exclude_none=True, response_model_by_alias=False)
# async def generateInvoiceLink(request: Request, id: str):
#     manager = getManager(request)
#     return await manager.generateInvoiceLink(id)

@router.delete("/business-details", response_model=SuccessResponse)
async def deleteBusinessDetails(request: Request):
    return await (await db(request)).user.deleteBusinessDetails()

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
