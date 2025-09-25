from typing import List, Optional
from pydantic import BaseModel, HttpUrl, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.model import PeriodDataRequest, Sort, Paginator, AnalyticValueFilterItem, LabelValue, PyObjectId, StartEndDate
from dzgroshared.db.products.model import Product, ProductCategory
from dzgroshared.db.enums import CollateType, AnalyticGroupMetricLabel, QueryTag

class ListingRequest(BaseModel):
    queryId: str
    categories: list[str] = []
    filters: list[AnalyticValueFilterItem] = []
    sort: Sort
    limit: int = 15
    skip: int = 0
    
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

class PerformanceDashboardResponseItem(BaseModel):
    tag: QueryTag
    curr: StartEndDate
    pre: StartEndDate
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

class PerformanceResultCategory(ProductCategory):
    count: int
    skus: List[Product]

class PerformanceResultParent(Product):
    count: int
    skus: List[Product]

class PerformanceResultAsin(Product):
    count: int|SkipJsonSchema[None] = None
    skus: List[Product]


class PerformanceTableResponseItem(BaseModel):
    data: list[PerformancePeriodGroup]
    category: PerformanceResultCategory|SkipJsonSchema[None] = None
    parent: PerformanceResultParent|SkipJsonSchema[None] = None
    asin: PerformanceResultAsin|SkipJsonSchema[None] = None
    sku: Product|SkipJsonSchema[None] = None   

class PerformanceTableResponse(BaseModel):
    rows: list[PerformanceTableResponseItem]
    columns: list[str]

     
class ComparisonTableRequest(BaseModel):
    queryId: PyObjectId
    collatetype: CollateType
    value: str|SkipJsonSchema[None]=None
    parent: str|SkipJsonSchema[None]=None
    filters: list[AnalyticValueFilterItem] = []
    paginator: Paginator = Paginator(skip=0, limit=10)
    sort: Sort = Sort(field='revenue', order=-1)

    @model_validator(mode="after")
    def checkValueOrParent(self):
        if self.collatetype==CollateType.MARKETPLACE:
            raise ValueError("'Marketplace' is not a valid collate type for this request.")
        else:
            if not self.value and not self.parent:
                raise ValueError("Either 'value' or 'parent' must be provided.")
            if self.collatetype == CollateType.CATEGORY and self.parent:
                raise ValueError("'parent' should not be provided when collatetype is 'CATEGORY'.")
            if self.collatetype == CollateType.PARENT and self.parent:
                raise ValueError("'parent' should not be provided when collatetype is 'PARENT'.")
        return self

class ComparisonPeriodDataRequest(PeriodDataRequest):
    queryId: PyObjectId