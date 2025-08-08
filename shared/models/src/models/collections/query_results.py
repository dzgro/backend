from pydantic import BaseModel, HttpUrl, model_validator
from pydantic.json_schema import SkipJsonSchema
from models.model import ItemId, Sort, Paginator, AnalyticValueFilterItem, LabelValue, PyObjectId
from models.collections.products import Product, ProductCategory
from models.enums import CollateType

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
    
class QueryResultKeyDetail(BaseModel):
    curr: str
    pre: str
    growth: str|SkipJsonSchema[None]=None
    growing: bool|SkipJsonSchema[None]=None

    @model_validator(mode="before")
    def setdefaults(cls, data):
        if 'curr' not in data: data['curr'] = "-"
        if 'pre' not in data: data['pre'] = "-"
        return data
class QueryTableResult(ItemId):
    data: QueryResultKeyDetail

class QueryResultItem(BaseModel):
    label: str
    data: QueryResultKeyDetail

    @model_validator(mode="before")
    def setdefaults(cls, data):
        if 'data' not in data: data['data'] = {}
        return data

class QueryResultGroup(BaseModel):
    label: str
    items: list[QueryResultItem]

class QueryResultChildren(ProductCategory):
    count: int
    skus: list[Product] = []

class QueryResultParent(QueryResultChildren, Product):
    count: int
    skus: list[Product] = []

class QueryResultAsin(QueryResultChildren, Product):
    count: int|SkipJsonSchema[None]=None

class QueryResult(BaseModel):
    data: list[QueryResultGroup]
    category: QueryResultChildren|SkipJsonSchema[None] = None
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
