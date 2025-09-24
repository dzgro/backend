
from dzgroshared.db.model import AnalyticPeriodGroup, AnalyticPeriodValuesGroup, MonthLite, MultiLevelColumns, ValueWithValueString
from pydantic import BaseModel



class ChartData(BaseModel):
    dates: list[str]
    values: list[float]

class MonthLiteResponseItem(BaseModel):
    month: str
    data: AnalyticPeriodGroup
    bars: AnalyticPeriodGroup
    meterGroups: list[AnalyticPeriodGroup]

class MonthLiteResponse(BaseModel):
    data: list[MonthLiteResponseItem]

class MonthTableResponse(BaseModel):
    columns: list[MonthLite]
    rows: list[AnalyticPeriodValuesGroup]

class MonthDateTableResponseRow(BaseModel):
    date: str
    values: list[ValueWithValueString]

class MonthDateTableResponse(BaseModel):
    columns: MultiLevelColumns
    rows: list[MonthDateTableResponseRow]

