from enum import Enum
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.model import ItemId, ObjectIdStr
from pydantic import BaseModel

class PaymentStatus(str, Enum):
    GENERATING_INVOICE = "generating_invoice"
    INVOICE_GENERATED = "invoice_generated"
    INVOICE_GENERATION_FAILED = "invoice_generation_failed"
    
class PaymentRequest(ObjectIdStr):
    paymentId: str
    amount: float
    gstrate: float

class Payment(PaymentRequest):
    pregst: float
    gst: float
    isRefund: bool|SkipJsonSchema[None]=None
    invoice: int
    invoicelink: str|SkipJsonSchema[None]=None
    status: PaymentStatus

class PaymentList(BaseModel):
    count: int|SkipJsonSchema[None]=None
    data: list[Payment]