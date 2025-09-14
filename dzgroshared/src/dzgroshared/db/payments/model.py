from enum import Enum
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.model import ItemId
from pydantic import BaseModel

class PaymentStatus(str, Enum):
    CAPTURED = "captured"
    GENERATING_INVOICE = "generating_invoice"
    INVOICE_GENERATED = "invoice_generated"
    INVOICE_GENERATION_FAILED = "invoice_generation_failed"
    


class Payment(ItemId):
    uid:str
    paymenttype: str
    amount: float
    isRefund: bool|SkipJsonSchema[None]=None
    invoice: int
    invoicelink: str|SkipJsonSchema[None]=None
    status: PaymentStatus

class PaymentList(BaseModel):
    count: int|SkipJsonSchema[None]=None
    data: list[Payment]