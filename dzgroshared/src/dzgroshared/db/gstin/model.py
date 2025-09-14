
from typing import List
from dzgroshared.db.enums import GSTStateCode
from dzgroshared.db.model import ItemId
from pydantic import BaseModel, Field

class BusinessDetails(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15)
    name: str
    addressline1: str
    addressline2: str
    addressline3: str
    pincode: str
    city: str
    state: GSTStateCode


class GSTDetail(ItemId, BusinessDetails):
    pass

class LinkedGSTs(BaseModel):
    data: List[GSTDetail]