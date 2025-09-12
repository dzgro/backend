from dzgroshared.models.razorpay.common import RazorpayId, Notes
from pydantic import BaseModel,Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from typing import Literal

class RazorpayCustomerEntity(Notes):
    name: str|SkipJsonSchema[None]=None
    email: str
    contact: str|SkipJsonSchema[None]=None

class RazorpayCustomer(RazorpayId, RazorpayCustomerEntity):
    gstin: str|SkipJsonSchema[None]=None
    created_at: int

class RazorpayCustomerList(BaseModel):
    items: list[RazorpayCustomer]
    count: int

class RazorpayCreateCustomer(RazorpayCustomerEntity):
    fail_existing: str = "0"

class RazorpayEditCustomer(BaseModel):
    name: str|SkipJsonSchema[None]=None
    email: str|SkipJsonSchema[None]=None
    contact: str|SkipJsonSchema[None]=None
