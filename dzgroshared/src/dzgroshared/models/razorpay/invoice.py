from dzgroshared.models.razorpay.common import ItemWithNameDescriptionCurrencyAmount, Notes,RazorpayPagination,RazorpayId, Currency, Amount, Receipt
from dzgroshared.models.razorpay.customer import RazorpayCustomer
from pydantic import BaseModel,Field
from pydantic.json_schema import SkipJsonSchema
from typing import List, Literal

class RazorpayLineItem(ItemWithNameDescriptionCurrencyAmount):
    quantity: int = Field(gt=0, default=1)


class RazorpayCreateInvoice(Currency, Notes):
    type: Literal["invoice"]
    description: str
    customer_id: str
    line_items: List[RazorpayLineItem]
    expire_by: int|SkipJsonSchema[None]=None
    sms_notify: bool = False
    email_notify: bool = False
    partial_payment: bool = False

class RazorpayInvoice(RazorpayId, Currency, Notes, Receipt):
    description: str|SkipJsonSchema[None]=None
    customer_id: str
    customer_details: RazorpayCustomer
    line_items: List[RazorpayLineItem]
    expire_by: int|SkipJsonSchema[None]=None
    created_at: int
    payment_id: str|SkipJsonSchema[None]=None
    amount_paid: int|SkipJsonSchema[None]=None
    amount_due: int|SkipJsonSchema[None]=None
    short_url: str|SkipJsonSchema[None]=None
    created_at: int
    status: Literal['draft','issued','paid','partially paid','cancelled','expired','deleted']
