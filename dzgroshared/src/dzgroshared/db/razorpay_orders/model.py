from enum import Enum
from dzgroshared.razorpay.order.model import RazorpayOrder
from pydantic import BaseModel

class RazorPayDbOrderCategory(str, Enum):
    MARKETPLACE_ONBOARDING = "MARKETPLACE_ONBOARDING"
    INVOICE = "INVOICE"

class RazorPayDbOrder(RazorpayOrder):
    category: RazorPayDbOrderCategory

class OrderVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str