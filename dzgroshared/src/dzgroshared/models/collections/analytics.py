from dzgroshared.models.collections.health import AmazonHealthReportConverted
from dzgroshared.models.model import MultiLevelColumns, PyObjectId
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import AnalyticGroupMetricLabel, AnalyticsMetric, AnalyticsPeriod, CollateType, CountryCode, QueryTag
from datetime import datetime
from typing import List, Literal, Optional

class MarketplaceHealthResponse(BaseModel):
    health: AmazonHealthReportConverted

class ValueWithValueString(BaseModel):
    value: float
    valueString: str

class AnalyticPeriodValuesItem(BaseModel):
    label: str
    values: list[ValueWithValueString]
    items: Optional[List["AnalyticPeriodValuesItem"]] = None  # recursive reference

    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
AnalyticPeriodValuesItem.model_rebuild()  # required for recursive models in Pydantic v2


class AnalyticPeriodItem(ValueWithValueString):
    label: str
    items: Optional[List["AnalyticPeriodItem"]] = None  # recursive reference

    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
AnalyticPeriodItem.model_rebuild()  # required for recursive models in Pydantic v2

class AnalyticPeriodGroup(BaseModel):
    label: AnalyticGroupMetricLabel
    items: list[AnalyticPeriodItem]

class AnalyticPeriodValuesGroup(BaseModel):
    label: AnalyticGroupMetricLabel
    items: list[AnalyticPeriodValuesItem]

class PeriodDataResponseItem(BaseModel):
    label: AnalyticsPeriod
    dateSpan: str
    data: list[AnalyticPeriodGroup]

class PeriodDataResponse(BaseModel):
    data: list[PeriodDataResponseItem]

class ChartData(BaseModel):
    dates: list[str]
    values: list[float]

class MonthLite(BaseModel):
    month: str
    period: str

class Month(MonthLite):
    startdate: datetime
    enddate: datetime


class PeriodDataRequest(BaseModel):
    collatetype: CollateType
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

class MonthDataResponse(BaseModel):
    month: str
    data: AnalyticPeriodGroup
    bars: AnalyticPeriodGroup
    meterGroups: list[AnalyticPeriodGroup]

class MonthTableResponse(BaseModel):
    columns: list[MonthLite]
    rows: list[AnalyticPeriodValuesGroup]

class MonthDateTableResponseRow(BaseModel):
    date: str
    values: list[ValueWithValueString]

class MonthDateTableResponse(BaseModel):
    columns: MultiLevelColumns
    rows: list[MonthDateTableResponseRow]

class StateMonthDataResponseItem(BaseModel):
    state: str
    data: list[AnalyticPeriodItem]

class StateMonthDataResponse(BaseModel):
    data: list[StateMonthDataResponseItem]

class StateDetailedDataByStateRequest(PeriodDataRequest):
    state: str

class StateDetailedDataResponse(BaseModel):
    columns: list[MonthLite]
    rows: list[AnalyticPeriodValuesGroup]

class AllStateDataItem(BaseModel):
    state: str
    values: list[ValueWithValueString]


class AllStateData(BaseModel):
    columns: MultiLevelColumns
    rows: list[AllStateDataItem]

class SingleAnalyticsMetricTableResponseItem(BaseModel):
    tag: QueryTag
    curr: str
    pre: str
    growth: str
    
class ComparisonPeriodDataRequest(PeriodDataRequest):
    queryId: PyObjectId
    
class PerformancePeriodItem(BaseModel):
    label: str
    value: str
    valueString: str
    growth: str
    growing: bool
    items: Optional[List["PerformancePeriodItem"]] = None  # recursive reference
    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
PerformancePeriodItem.model_rebuild()  # required for recursive models in Pydantic v2

class PerformancePeriodGroup(BaseModel):
    label: AnalyticGroupMetricLabel
    items: list[PerformancePeriodItem]

class PerformancePeriodData(BaseModel):
    headers: list[AnalyticGroupMetricLabel]
    items: list[PerformancePeriodGroup]

class PerformancePeriodDataResponse(BaseModel):
    data: list[PerformancePeriodGroup]






    

