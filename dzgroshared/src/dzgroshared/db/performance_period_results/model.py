from typing import List, Optional
from dzgroshared.db.performance_periods.model import PerformancePeriod
from pydantic import BaseModel, HttpUrl, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.model import MultiLevelColumns, PeriodDataRequest, RowColumnSpan, Sort, Paginator, AnalyticValueFilterItem, LabelValue, PyObjectId, StartEndDate
from dzgroshared.db.products.model import PerformanceResultCategory, PerformanceResultParent, PerformanceResultAsin, PerformanceResultSku, Product, ProductCategory, VariationTheme
from dzgroshared.db.enums import CollateType, AnalyticGroupMetricLabel, QueryTag

class ListingRequest(BaseModel):
    queryId: str
    categories: list[str] = []
    filters: list[AnalyticValueFilterItem] = []
    sort: Sort
    limit: int = 15
    skip: int = 0

class PerformanceResultValue(BaseModel):
    value: str
    valueString: str
    growth: str
    growing: bool

    
class PerformancePeriodItem(PerformanceResultValue):
    label: str
    items: Optional[List["PerformancePeriodItem"]] = None  # recursive reference
    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
PerformancePeriodItem.model_rebuild()  # required for recursive models in Pydantic v2

class PerformanceTableLiteResponseSubItem(RowColumnSpan):
    label: str
    values: list[PerformanceResultValue]
    items: Optional[List["PerformanceTableLiteResponseSubItem"]] = None  # recursive reference
    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
PerformanceTableLiteResponseSubItem.model_rebuild()

class PerformanceTableLiteResponseItem(RowColumnSpan):
    label: AnalyticGroupMetricLabel
    items: list[PerformanceTableLiteResponseSubItem]


class PerformancePeriodGroup(BaseModel):
    label: AnalyticGroupMetricLabel
    items: list[PerformancePeriodItem]

class PerformancePeriodData(BaseModel):
    headers: list[AnalyticGroupMetricLabel]
    items: list[PerformancePeriodGroup]

class PerformanceDashboardResponseItem(PerformancePeriod):
    data: list[PerformancePeriodGroup]

class PerformanceDashboardResponse(BaseModel):
    data: list[PerformanceDashboardResponseItem]


class ListingResponse(BaseModel):
    product: Product

class CategoriesByKey(Sort):
    queryId: str

class CategoryCount(ProductCategory):
    count: int

class ProductPerformanceFilterMetric(BaseModel):
    metrics: list[LabelValue]
    operators: list[LabelValue]
    queryTypes: list[LabelValue]
    sortTypes: list[LabelValue]

class CategoryQueryResultItem(ProductCategory):
    count: int
    moreCount: int
    asins: list[Product]

    @model_validator(mode="before")
    def setMoreCount(cls, data: dict):
        data['moreCount'] = data['count'] - len(data['asins'])
        return data


class PerformanceTableResponseItem(BaseModel):
    data: list[PerformancePeriodGroup]
    category: PerformanceResultCategory|SkipJsonSchema[None] = None
    parent: PerformanceResultParent|SkipJsonSchema[None] = None
    asin: PerformanceResultAsin|SkipJsonSchema[None] = None
    sku: PerformanceResultSku|SkipJsonSchema[None] = None

class PerformanceTableResponse(BaseModel):
    rows: list[PerformanceTableResponseItem]
    columns: list[str]

class PerformanceTableLiteResponse(BaseModel):
    rows: list[PerformanceTableLiteResponseItem]
    columns: MultiLevelColumns
     
class ComparisonTableRequest(BaseModel):
    queryId: PyObjectId
    parentsku: str|SkipJsonSchema[None] = None
    category: str|SkipJsonSchema[None] = None
    collatetype: CollateType
    filters: list[AnalyticValueFilterItem] = []
    paginator: Paginator
    sort: Sort

    @model_validator(mode="after")
    def checkValueOrParent(self):
        if self.collatetype==CollateType.MARKETPLACE:
            raise ValueError("'Marketplace' is not a valid collate type for this request.")
        return self
    
class ComparisonTableRequestWithValue(ComparisonTableRequest):
    value: str

class ComparisonPeriodDataRequest(PeriodDataRequest):
    queryId: PyObjectId