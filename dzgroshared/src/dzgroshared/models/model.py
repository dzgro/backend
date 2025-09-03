from pydantic_core import core_schema
from pydantic import BaseModel,Field, ConfigDict, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import CountryCode, MarketplaceId, AmazonAccountType, CollateTypeTag, CollectionType
from typing import Any, Optional, Literal
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

class ItemIdWithDate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
    id: PyObjectId= Field(...,alias="_id")
    createdat: datetime|SkipJsonSchema[None]=None
    @model_validator(mode="before")
    def setCreateAt(cls, data):
        data['createdat'] = ObjectId(str(data['_id'])).generation_time
        return data

class ItemObjectId(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
    id: ObjectId= Field(alias="_id")

class MarketplaceObjectId(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
    marketplace: PyObjectId= Field(default_factory=PyObjectId)

class ObjectIdStr(BaseModel):
    # model_config = ConfigDict(alias_generator=lambda name: '_'+name)
    id: str = Field(..., alias="_id")

class CustomError(Exception):
    def __init__(self, error_data: dict):
        self.error_data = error_data
        super().__init__(str(error_data))


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
    code: int = Field(..., description="Error code returned by the API")
    message: str|SkipJsonSchema[None] = None
    details: str|SkipJsonSchema[None] = None
    description: str|SkipJsonSchema[None] = None
    source: str|SkipJsonSchema[None] = None
    step: str|SkipJsonSchema[None] = None
    reason: str|SkipJsonSchema[None] = None
    metadata: dict|SkipJsonSchema[None] = None

class ErrorList(BaseModel):
    errors: list[ErrorDetail] = Field(..., description="List of errors returned by the API")
    status_code: int = 500


class DzgroError(Exception):
    def __init__(self, error_list: ErrorList, status_code: int = 500):
        self.error_list = error_list
        self.status_code = status_code
        super().__init__(str(error_list))


SATKey =  Literal['sales','ad','traffic']



class LabelValue(BaseModel):
    label: str
    value:str
    icon:str|SkipJsonSchema[None]=None

class AnalyticKeyGroup(BaseModel):
    label: str
    items: list[LabelValue]

class QueryId(BaseModel):
    queryId: PyObjectId


class AnalyticValueFilterItem(BaseModel):
    metric: str
    operator: str
    value: float

class ValueWithRawValue(BaseModel):
    value: str
    rawvalue: float

class AnalyticsLabelValue(BaseModel):
    label: str
    key: str
    value: ValueWithRawValue

class AnalyticsGroup(BaseModel):
    label: str
    items: list[AnalyticsLabelValue]

class AnalyticsPeriodData(BaseModel):
    period: str
    dates: str
    data: list[AnalyticsGroup]

class ChartData(BaseModel):
    dates: list[str]
    values: list[float]

class Count(BaseModel):
    count: int

class OperatorWithSigns(BaseModel):
    label:str
    value: str

class AuthorizationUrlRequest(BaseModel):
    name: str
    countryCode: CountryCode
    accountType: AmazonAccountType
class Url(BaseModel):
    url: str

class AddMarketplace(BaseModel):
    seller: str
    ad: str
    sellerid: str
    marketplaceid: MarketplaceId
    countrycode: CountryCode
    storename: str
    profileid: int


class AdAccount(BaseModel):
    accountname: str
    entityid: str
    countryCode: CountryCode
    profileid: int
    adsaccountid: str


class AdvertisingAccountInfo(BaseModel):
    marketplaceStringId: str
    id: str
    type: str
    name: str
    validPaymentMethod: bool

class AdvertisingProfile(BaseModel):
    profileId: int
    countryCode: str
    currencyCode: str
    timezone: str
    accountInfo: AdvertisingAccountInfo


class DzgroSecrets(BaseModel):
    COGNITO_APP_CLIENT_ID: str
    COGNITO_USER_POOL_ID: str
    RAZORPAY_CLIENT_ID: str
    RAZORPAY_CLIENT_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str
    SPAPI_CLIENT_ID: str
    SPAPI_CLIENT_SECRET: str
    SPAPI_APPLICATION_ID: str
    ADS_CLIENT_ID: str
    ADS_CLIENT_SECRET: str
    MONGO_DB_CONNECT_URI: str
    MONGO_DB_FED_CONNECT_URI: str

DataCollections: list[CollectionType] = [
            # CollectionType.ORDERS,
            # CollectionType.ORDER_ITEMS,
            # CollectionType.SETTLEMENTS,
            CollectionType.ADV,
            # CollectionType.PRODUCTS,
            # CollectionType.ADV_ASSETS,
            CollectionType.ADV_ADS,
            CollectionType.ADV_RULE_RUNS,
            CollectionType.ADV_RULE_RUN_RESULTS,
            CollectionType.STATE_ANALYTICS,
            CollectionType.DATE_ANALYTICS,
            CollectionType.QUERY_RESULTS,
            CollectionType.DZGRO_REPORT_DATA,
            CollectionType.DZGRO_REPORTS,
            CollectionType.HEALTH,
            # CollectionType.TRAFFIC,
            CollectionType.QUEUE_MESSAGES,
            CollectionType.AMAZON_CHILD_REPORT,
            CollectionType.AMAZON_CHILD_REPORT_GROUP,
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