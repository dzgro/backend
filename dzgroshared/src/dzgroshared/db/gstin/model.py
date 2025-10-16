
from typing import List
from dzgroshared.db.enums import GstStateCode
from dzgroshared.db.model import ItemId
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema

class GstStateResponse(BaseModel):
    state: str
    statecode: GstStateCode

class BusinessDetails(GstStateResponse):
    gstin: str = Field(..., min_length=15, max_length=15)
    name: str
    addressline1: str
    addressline2: str
    addressline3: str
    pincode: str
    city: str
    
    @model_validator(mode="before")
    def check_gstin(cls, values):
        gstin = values.get("gstin")
        state_code = gstin[0:2]
        if not values.get("statecode"): values["statecode"] = GstStateCode(state_code)
        if not values.get("state"): values["state"] = GstStateCode.get_state_name(state_code)
        return values


class GstDetail(ItemId, BusinessDetails):
    pass

class LinkedGsts(BaseModel):
    data: List[GstDetail]