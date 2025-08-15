from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import CollateType
from datetime import datetime
from typing import Literal


class CollateTypeAndValue(BaseModel):
    collatetype: CollateType
    value: str|SkipJsonSchema[None]=None
    
class Label(BaseModel):
    label: str

class StringValue(BaseModel):
    value: str

class LabelStringValue(Label, StringValue):
    pass

class MonthWithDates(BaseModel):
    monthStr: str
    month: int
    year: int
    period: str

class MonthData(Label):
    label: str
    key: str
    data: list[str]
class StateData(BaseModel):
    state: str
    data: list[LabelStringValue]

class MonthCarouselLabelValue(Label):
    value:str|float
    icon: str|SkipJsonSchema[None]=None
    color: str|SkipJsonSchema[None]=None

class MonthCarouselLabelValueGroup(Label):
    items: list[MonthCarouselLabelValue]

class MonthlyCarousel(BaseModel):
    keymetrics: list[MonthCarouselLabelValue]
    bars: list[MonthCarouselLabelValue]
    groups: list[MonthCarouselLabelValueGroup]






    

