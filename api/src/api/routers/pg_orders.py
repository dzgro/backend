from dzgroshared.models.collections.pg_orders import OrderVerificationRequest
from fastapi import APIRouter, Request, Depends
from api.Util import RequestHelper
from dzgroshared.models.model import SuccessResponse
router = APIRouter(prefix="/pg", tags=["Payment Gateway"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.pg_orders


@router.post("/verify/order", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def getPaymentObject(request: Request, req: OrderVerificationRequest):
    return await (await db(request)).verifyOrder(req)