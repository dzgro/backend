from fastapi import APIRouter, Request, Depends
from api.Util import RequestHelper
from dzgroshared.db.model import SuccessResponse
from dzgroshared.db.razorpay_orders.model import OrderVerificationRequest
router = APIRouter(prefix="/pg", tags=["Payment Gateway"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.razorpay_orders


@router.post("/verify/order", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def verifyOrder(request: Request, req: OrderVerificationRequest):
    return await (await db(request)).verifyOrder(req)