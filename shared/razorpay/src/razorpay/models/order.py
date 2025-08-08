from razorpay.models.common import Notes,RazorpayPagination,RazorpayId, Currency, Amount
from pydantic import BaseModel,Field
from pydantic.json_schema import SkipJsonSchema
from typing import Literal

class Receipt(BaseModel):
    receipt: str

class Order(RazorpayId, Currency, Notes, Amount, Receipt):
    partial_payment: bool|SkipJsonSchema[None]=None
    amount_paid: int
    amount_due: int
    status: Literal['created','attempted','paid']
    attempts: int
    created_at: int

class CreateOrder(Currency, Notes, Amount):
    receipt: str
    partial_payment: bool = Field(default=False)
    first_payment_min_amount: int|SkipJsonSchema[None]=None

class FetchOrders(RazorpayPagination, Receipt):
    authorized: bool

class FetchOrderById(RazorpayId):
    pass

class FetchPaymentForOrderById(RazorpayId):
    pass

class UpdateOrder(RazorpayId, Notes):
    pass

