from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.model import ItemIdWithDate
from pydantic import BaseModel
class Payment(ItemIdWithDate):
    uid:str
    paymenttype: str
    amount: float
    isRefund: bool|SkipJsonSchema[None]=None
    invoice: int
    invoicelink: str|SkipJsonSchema[None]=None

class Payments(BaseModel):
    count: int
    payments: list[Payment]