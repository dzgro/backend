from enum import Enum
from dzgroshared.db.model import MarketplacePlan, ObjectIdStr, PyObjectId
from dzgroshared.db.pricing.model import PlanName
from dzgroshared.razorpay.order.model import RazorPayOrderNotes, RazorpayOrder
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class RazorPayDbOrderCategory(str, Enum):
    MARKETPLACE_ONBOARDING = "MARKETPLACE_ONBOARDING"
    INVOICE = "INVOICE"

class RazorPayDbOrder(ObjectIdStr):
    amount: float
    category: RazorPayDbOrderCategory
    invoiceId: str|SkipJsonSchema[None]=None
    paymentId: str|SkipJsonSchema[None]=None
    notes: RazorPayOrderNotes


class OrderVerificationRequest(BaseModel):
    razorpayOrderId: str
    razorpayPaymentId: str
    razorpaySignature: str
    marketplace: PyObjectId