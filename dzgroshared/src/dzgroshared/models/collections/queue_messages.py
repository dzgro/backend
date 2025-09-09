from dzgroshared.models.collections.queries import Query
from dzgroshared.models.model import MarketplaceObjectId, PyObjectId
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from bson import ObjectId
from dzgroshared.models.enums import AmazonDailyReportAggregationStep, CountryCode, QueueName
from typing import Type, Union
from dzgroshared.models.collections.dzgro_reports import DzgroReportType

class MessageIndexOptional(BaseModel):
    index: str|SkipJsonSchema[None]=None

class MessageIndex(BaseModel):
    index: str

class AmazonParentReportQueueMessage(MessageIndexOptional, MarketplaceObjectId):
    step: AmazonDailyReportAggregationStep
    date: datetime|SkipJsonSchema[None]=None

class DzgroReportQueueMessage(MessageIndex, MarketplaceObjectId):
    reporttype: DzgroReportType

class PaymentMessage(MessageIndex):
    uid: str
    amount:float
    gst: int
    date: datetime

class DailyReportMessage(BaseModel):
    index: CountryCode
    success: int|SkipJsonSchema[None]=None
    failed: int|SkipJsonSchema[None]=None
    total: int|SkipJsonSchema[None]=None

class UserDetails(BaseModel):
    name: str
    email: str
    phone: str|SkipJsonSchema[None]=None
    userpoolid: str

class NewUserQueueMessage(BaseModel):
    uid: str
    details: UserDetails

QueueMessageModel = Union[AmazonParentReportQueueMessage, NewUserQueueMessage, DzgroReportQueueMessage, PaymentMessage]

MODEL_REGISTRY: dict[str, Type[QueueMessageModel]] = {
    "AmazonParentReportQueueMessage": AmazonParentReportQueueMessage,
    "NewUserQueueMessage": NewUserQueueMessage,
    "DzgroReportQueueMessage": DzgroReportQueueMessage,
    "PaymentMessage": PaymentMessage,
}
