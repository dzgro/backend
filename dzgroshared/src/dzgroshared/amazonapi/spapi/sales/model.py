from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from dzgroshared.db.model import ErrorDetail

class Granularity(str, Enum):
    HOUR = "Hour"
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"
    YEAR = "Year"
    TOTAL = "Total"

class BuyerType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"
    ALL = "All"

class FirstDayOfWeek(str, Enum):
    MONDAY = "Monday"
    SUNDAY = "Sunday"

class Money(BaseModel):
    currency_code: str = Field(..., alias="currencyCode")
    amount: float

class OrderMetricsInterval(BaseModel):
    interval: str
    unit_count: int = Field(..., alias="unitCount")
    order_item_count: int = Field(..., alias="orderItemCount")
    order_count: int = Field(..., alias="orderCount")
    average_unit_price: Money = Field(..., alias="averageUnitPrice")
    total_sales: Money = Field(..., alias="totalSales")

class GetOrderMetricsResponse(BaseModel):
    payload: Optional[List[OrderMetricsInterval]] = None
    errors: Optional[List[ErrorDetail]] = None 