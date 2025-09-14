
from dzgroshared.db.model import AnalyticPeriodItem, AnalyticPeriodValuesGroup, MonthLite, MultiLevelColumns, PeriodDataRequest, ValueWithValueString
from pydantic import BaseModel


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