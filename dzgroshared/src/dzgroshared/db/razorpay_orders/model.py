from enum import Enum
from dzgroshared.db.enums import PlanType
from dzgroshared.db.model import ObjectIdStr, PyObjectId
from dzgroshared.razorpay.order.model import RazorpayOrder
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class RazorPayDbOrderCategory(str, Enum):
    MARKETPLACE_ONBOARDING = "MARKETPLACE_ONBOARDING"
    INVOICE = "INVOICE"

class RazorPayDbOrder(ObjectIdStr):
    amount: int
    category: RazorPayDbOrderCategory
    gstin: PyObjectId|SkipJsonSchema[None]=None
    invoiceId: str|SkipJsonSchema[None]=None
    paymentId: str|SkipJsonSchema[None]=None
    plantype: PlanType|SkipJsonSchema[None]=None
    pricing: PyObjectId|SkipJsonSchema[None]=None


class OrderVerificationRequest(BaseModel):
    razorpayOrderId: str
    razorpayPaymentId: str
    razorpaySignature: str
    marketplace: PyObjectId