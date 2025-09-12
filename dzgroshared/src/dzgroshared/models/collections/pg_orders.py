from enum import Enum
from dzgroshared.models.razorpay.order import RazorpayOrder
from pydantic import BaseModel

class PGOrderCategory(str, Enum):
    MARKETPLACE_ONBOARDING = "MARKETPLACE_ONBOARDING"
    INVOICE = "INVOICE"

class PGOrder(RazorpayOrder):
    category: PGOrderCategory

class OrderVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str