from pydantic_core import core_schema
from pydantic import BaseModel,Field, ConfigDict, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.enums import AnalyticsPeriod, CollateType, CountryCode, AnalyticGroupMetricLabel, MarketplaceId, AmazonAccountType, QueryTag, CollectionType, AnalyticsMetricOperation, AnalyticsMetric
from typing import Any, List, Optional, Literal
from bson import ObjectId
from datetime import datetime

SortOrder = Literal[1,-1]

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type, _handler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x), when_used="json"
            ),
        )

    @classmethod
    def validate(cls, value) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

class Paginator(BaseModel):
    skip:int
    limit:int

class Sort(BaseModel):
    field: str
    order: SortOrder

async def pagination(skip: int, limit: int)->dict:
    return {"skip": skip, "limit": limit}

class SuccessResponse(BaseModel):
    success: bool
    message: str|SkipJsonSchema[None] = None
    data: dict|SkipJsonSchema[None] = None
    route: str|SkipJsonSchema[None] = None

class ItemId(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
    id: PyObjectId= Field(...,alias="_id")                                                                                                                                         

class ItemObjectId(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
    id: ObjectId= Field(alias="_id")

class MarketplaceObjectId(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
    marketplace: PyObjectId= Field(default_factory=PyObjectId)

class ObjectIdStr(BaseModel):
    # model_config = ConfigDict(alias_generator=lambda name: '_'+name)
    id: str = Field(..., alias="_id")

class RefreshToken(BaseModel):
    refreshtoken: str

class LambdaContext:
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: Optional[Any]
    client_context: Optional[Any]

    def get_remaining_time_in_millis(self) -> int:
        ...


class ObjectIdModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    @model_validator(mode="before")
    @classmethod
    def convert_objectids(cls, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and ObjectId.is_valid(value):
                    data[key] = ObjectId(value)
        return data

from typing import Optional, Any

class MockLambdaContext(LambdaContext):
    def __init__(
        self,
        startTime: int = int(datetime.now().timestamp()*1000),
        function_name: str = "test_function",
        function_version: str = "$LATEST",
        invoked_function_arn: str = "arn:aws:lambda:us-east-1:123456789012:function:test_function",
        memory_limit_in_mb: int = 128,
        aws_request_id: str = "test-request-id",
        log_group_name: str = "/aws/lambda/test_function",
        log_stream_name: str = "2025/07/04/[$LATEST]abcdef1234567890",
        identity: Optional[Any] = None,
        client_context: Optional[Any] = None,
    ):
        self.function_name = function_name
        self.function_version = function_version
        self.invoked_function_arn = invoked_function_arn
        self.memory_limit_in_mb = memory_limit_in_mb
        self.aws_request_id = aws_request_id
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.identity = identity
        self.client_context = client_context
        self.startTime = startTime

    def get_remaining_time_in_millis(self) -> int:
        remaining = 900000 - (int(datetime.now().timestamp()*1000)-self.startTime)
        return remaining

class CountryDetails(BaseModel):
    countryCode: CountryCode = Field(..., alias="_id")
    marketplaceId: MarketplaceId
    currencyCode: str
    country: str
    region: str
    regionName: str
    timezone: str

    
class RequestObject(BaseModel):
    proxy: str
    method: str
    body: dict = {}
    params: dict = {}




class ErrorDetail(BaseModel):
    code: int = 500
    message: str|SkipJsonSchema[None] = None
    details: str|SkipJsonSchema[None] = None
    description: str|SkipJsonSchema[None] = None
    source: str|SkipJsonSchema[None] = None
    step: str|SkipJsonSchema[None] = None
    reason: str|SkipJsonSchema[None] = None
    metadata: dict|SkipJsonSchema[None] = None

class ErrorList(BaseModel):
    errors: list[ErrorDetail] = Field(..., description="List of errors returned by the API")


class DzgroError(Exception):
    def __init__(self, errors: ErrorList, status_code: int=500):
        self.errors = errors
        self.status_code= status_code
        super().__init__(str(errors))


SATKey =  Literal['sales','ad','traffic']

class LabelValue(BaseModel):
    label: str
    value: str

class AnalyticKeylabelValue(BaseModel):
    label: str
    value: AnalyticsMetric

class AnalyticKeyGroup(BaseModel):
    label: AnalyticGroupMetricLabel
    items: list[AnalyticKeylabelValue]

class QueryId(BaseModel):
    queryId: PyObjectId


class AnalyticValueFilterItem(BaseModel):
    metric: str
    operator: str
    value: float

class Count(BaseModel):
    count: int

class OperatorWithSigns(BaseModel):
    label:str
    value: str

class Url(BaseModel):
    url: str

class AddMarketplaceRequest(BaseModel):
    seller: PyObjectId
    ad: PyObjectId
    sellerid: str
    marketplaceid: MarketplaceId
    countrycode: CountryCode
    storename: str
    profileid: int

DataCollections: list[CollectionType] = [
            # CollectionType.ORDERS,
            # CollectionType.ORDER_ITEMS,
            # CollectionType.SETTLEMENTS,
            CollectionType.ADV_PERFORMANCE,
            # CollectionType.PRODUCTS,
            # CollectionType.ADV_ASSETS,
            CollectionType.ADV_ADS,
            CollectionType.ADV_RULE_RUNS,
            CollectionType.ADV_RULE_RUN_RESULTS,
            CollectionType.STATE_ANALYTICS,
            CollectionType.DATE_ANALYTICS,
            CollectionType.PERFORMANCE_PERIOD_RESULTS,
            CollectionType.DZGRO_REPORT_DATA,
            CollectionType.DZGRO_REPORTS,
            CollectionType.HEALTH,
            # CollectionType.TRAFFIC,
            CollectionType.QUEUE_MESSAGES,
            CollectionType.DAILY_REPORT_GROUP,
            CollectionType.DAILY_REPORT_ITEM,
        ]

class StartEndDate(BaseModel):
    startdate: datetime
    enddate: datetime
    label: str = ''

    @model_validator(mode="after")
    def setLabel(self):
        if self.startdate > self.enddate:
            raise ValueError("Date range is invalid")
        self.label = f'{self.startdate.strftime("%b %d, %Y")} - {self.enddate.strftime("%b %d, %Y")}'
        return self
    

    
class MetricCalculation(BaseModel):
    metric: AnalyticsMetric
    operation: AnalyticsMetricOperation
    metrics: list[AnalyticsMetric]
    avoidMultiplier: bool = False
    level: int = 0 # 0 for top-level, 1 for second-level, etc.

class MetricDetail(BaseModel):
    metric: AnalyticsMetric
    ispercentage: bool
    isReverseGrowth: bool = False
    label: str
    description: str|SkipJsonSchema[None] = None

class NestedColumn(BaseModel):
    header: str
    colSpan: int = 1


class MultiLevelColumns(BaseModel):
    columns1: list[NestedColumn]
    columns2: list[NestedColumn]|SkipJsonSchema[None]=None
    columns3: list[NestedColumn]|SkipJsonSchema[None]=None


class MetricItem(BaseModel):
    metric: AnalyticsMetric
    label: str|SkipJsonSchema[None] = None
    items: Optional[List["MetricItem"]] = None  # recursive reference
    
    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"
MetricItem.model_rebuild()

class MetricGroup(BaseModel):
    metric: AnalyticGroupMetricLabel
    items: list[MetricItem]


class RenameAccountRequest(ItemId):
    name: str


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
    
class PeriodDataRequest(BaseModel):
    collatetype: CollateType
    value: str|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def checkValue(self):
        if self.collatetype!=CollateType.MARKETPLACE and (self.value is None or self.value.strip()==""):
            raise ValueError("Value must be provided when collate type is not marketplace")
        return self
    


class MonthLite(BaseModel):
    month: str
    period: str

class Month(MonthLite):
    startdate: datetime
    enddate: datetime

class SingleMetricPeriodDataRequest(PeriodDataRequest):
    key: AnalyticsMetric

class MonthDataRequest(PeriodDataRequest):
    month: str