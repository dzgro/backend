from typing import List, Optional
from dzgroshared.models.collections.analytics import PerformancePeriodGroup
from pydantic import BaseModel, HttpUrl, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.model import ItemId, Sort, Paginator, AnalyticValueFilterItem, LabelValue, PyObjectId
from dzgroshared.models.collections.products import Product, ProductCategory
from dzgroshared.models.enums import CollateType, AnalyticGroupMetricLabel, QueryTag

class ListingRequest(BaseModel):
    queryId: str
    categories: list[str] = []
    filters: list[AnalyticValueFilterItem] = []
    sort: Sort
    limit: int = 15
    skip: int = 0


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

class PerformanceResultChildren(ProductCategory):
    count: int
    skus: list[Product] = []

class QueryResultParent(PerformanceResultChildren, Product):
    count: int
    skus: list[Product] = []

class QueryResultAsin(PerformanceResultChildren, Product):
    count: int|SkipJsonSchema[None]=None

class QueryResult(BaseModel):
    data: list[PerformancePeriodGroup]
    category: PerformanceResultChildren|SkipJsonSchema[None] = None
    parent: QueryResultParent|SkipJsonSchema[None] = None
    asin: QueryResultAsin|SkipJsonSchema[None] = None
    sku: Product|SkipJsonSchema[None] = None   
     
class QueryRequest(BaseModel):
    queryId: str
    collateType: CollateType
    value: str|SkipJsonSchema[None]=None
    parent: str|SkipJsonSchema[None]=None
    category: str|SkipJsonSchema[None]=None
    filters: list[AnalyticValueFilterItem] = []
    paginator: Paginator = Paginator(skip=0, limit=10)
    sort: Sort = Sort(field='revenue', order=-1)

class ComparisonTableResult(ItemId):
    data: PerformancePeriodGroup