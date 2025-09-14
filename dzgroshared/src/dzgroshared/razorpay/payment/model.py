
from dzgroshared.razorpay.common import Notes,RazorpayPagination,RazorpayId, Currency, Amount, RazorpayEntity,snakeCaseToTitleCase
from pydantic import BaseModel, ConfigDict,Field
from pydantic.json_schema import SkipJsonSchema
from typing import Literal,Any

class RazorpayCard(RazorpayId,RazorpayEntity):
    model_config = snakeCaseToTitleCase()
    name: str
    last4: str
    network: str|Literal['American Express','Diners Club','Unknown','Maestro','MasterCard','UnionPay','Visa']
    type: str|Literal['credit','debit','prepaid', 'unknown']
    issuer: str|SkipJsonSchema[None]=None
    emi: bool
    sub_type: str|Literal['customer','business','consumer']

class RazorpayUpi(BaseModel):
    payer_account_type: Literal['bank_account','credit_card','wallet']
    vpa: str
    flow: str

class RazorpayPayment(RazorpayId, RazorpayEntity,Currency, Amount, Notes):
    model_config = snakeCaseToTitleCase()
    status: Literal['created','authorized','captured','refunded','failed']
    method: Literal['card','netbanking','wallet','emi','upi','neft','imps','rtgs','cash','cheque','demand_draft','other']
    amount_refunded: int
    amount_transferred: int|SkipJsonSchema[None]=None
    refund_status: Literal['null','partial','full']|SkipJsonSchema[None]=None
    order_id:str
    invoice_id: str
    international: bool
    captured: str|bool|SkipJsonSchema[None]=None
    card_id: str|SkipJsonSchema[None]=None
    card: RazorpayCard|SkipJsonSchema[None]=None
    upi: RazorpayUpi|SkipJsonSchema[None]=None
    bank: str|SkipJsonSchema[None]=None
    wallet: str|SkipJsonSchema[None]=None
    vpa: str|SkipJsonSchema[None]=None
    email: str
    contact: str
    created_at: int
    fee: int
    tax: int
    error_code: str|SkipJsonSchema[None]=None
    error_description: str|SkipJsonSchema[None]=None
    error_source: str|SkipJsonSchema[None]=None
    error_step: str|SkipJsonSchema[None]=None
    error_reason: str|SkipJsonSchema[None]=None
    acquirer_data: Any|SkipJsonSchema[None]=None

class CapturePayment(RazorpayId):
    pass

class FetchPaymentById(RazorpayId):
    pass

class FetchPayments(RazorpayPagination):
    pass

class UpdatePayment(RazorpayId, Notes):
    pass