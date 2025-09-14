from dzgroshared.razorpay.common import Notes,RazorpayPagination,RazorpayId
from pydantic import BaseModel,Field
from pydantic.json_schema import SkipJsonSchema
from typing import Literal

class AddOnEntity(BaseModel):
    name: str
    amount: int
    currency: str|SkipJsonSchema[None] = 'INR'



class AddOnWithDescription(BaseModel):
    description: str

class AddOnItem(BaseModel):
    item: AddOnEntity

class AddOnItemWithDescription(BaseModel):
    item: AddOnWithDescription

class CreateAddOn(RazorpayId):
    item: AddOnItemWithDescription
    quantity: int = Field(default=1)


class FetchAddOns(RazorpayPagination):
    pass

class FetchAddOnById(RazorpayId):
    pass

class DeleteAddOn(RazorpayId):
    pass


class AddOn(RazorpayId):
    quantity: int

