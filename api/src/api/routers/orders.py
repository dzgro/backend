from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.db.orders.model import OrderPaymentRequest, OrderPaymentList, OrderPaymentFacets

router = APIRouter(prefix="/orders", tags=["Orders"])


async def db(request: Request):
    """Helper to access orders database controller"""
    return (await RequestHelper(request).client).db.orders


@router.post(
    "/payments",
    response_model=OrderPaymentList,
    response_model_exclude_none=True,
    response_model_by_alias=False,
    summary="Get orders with payment settlement details"
)
async def getOrderPayments(request: Request, req: OrderPaymentRequest):
    """
    Retrieve orders with settlement details including:
    - Payment status (PAID, UNPAID, PENDING_SETTLEMENT, OVERDUE)
    - Shipping status (DELIVERED, RETURNED, PARTIAL_RETURNED)
    - SKU-level settlement breakdown
    - Non-SKU settlements (shipping, fees)
    """
    return await (await db(request)).getOrderPayments(req)


@router.post(
    "/facets",
    response_model=OrderPaymentFacets,
    response_model_exclude_none=True,
    response_model_by_alias=False,
    summary="Get payment status facet counts"
)
async def getOrderPaymentFacets(request: Request, req: OrderPaymentRequest):
    """
    Get counts of orders grouped by payment status.
    Used for dashboard summary cards.
    """
    return await (await db(request)).getOrderPaymentFacets(req)
