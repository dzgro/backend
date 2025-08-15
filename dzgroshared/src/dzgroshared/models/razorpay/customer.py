from dzgroshared.models.razorpay.common import RazorpayId, Notes
from pydantic import BaseModel,Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from typing import Literal

class CustomerEntity(Notes):
    name: str|SkipJsonSchema[None]=None
    email: str
    contact: str|SkipJsonSchema[None]=None

class Customer(RazorpayId, CustomerEntity):
    gstin: str|SkipJsonSchema[None]=None
    created_at: int

class CustomerList(BaseModel):
    items: list[Customer]
    count: int

class CreateCustomer(CustomerEntity):
    fail_existing: str = "0"

class EditCustomer(BaseModel):
    name: str|SkipJsonSchema[None]=None
    email: str|SkipJsonSchema[None]=None
    contact: str|SkipJsonSchema[None]=None
