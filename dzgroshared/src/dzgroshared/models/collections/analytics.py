from bson import ObjectId
from dzgroshared.models.model import ObjectIdModel, PyObjectId
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import AnalyticsMetric, CollateType, CountryCode, QueryTag
from datetime import datetime
from typing import Literal


class PeriodDataRequest(BaseModel):
    collatetype: CollateType
    countrycode: CountryCode
    value: str|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def checkValue(self):
        if self.collatetype!=CollateType.MARKETPLACE and (self.value is None or self.value.strip()==""):
            raise ValueError("Value must be provided when collate type is not marketplace")
        return self
    
class SingleMetricPeriodDataRequest(PeriodDataRequest):
    key: AnalyticsMetric

class MonthDataRequest(PeriodDataRequest):
    month: str

    
class SingleAnalyticsMetricTableResponseItem(BaseModel):
    tag: QueryTag
    curr: str
    pre: str
    growth: str
    
class ComparisonPeriodDataRequest(PeriodDataRequest):
    queryId: PyObjectId

    
class Label(BaseModel):
    label: str

class StringValue(BaseModel):
    value: str

class LabelStringValue(Label, StringValue):
    pass

class Month(BaseModel):
    month: str
    period: str
    startdate: datetime
    enddate: datetime

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






    

