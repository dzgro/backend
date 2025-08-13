from models.collections.queries import Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from bson import ObjectId
from models.enums import AmazonDailyReportAggregationStep
from typing import Type
from models.collections.dzgro_reports import DzgroReportType

class MessageIndexOptional(BaseModel):
    index: str|SkipJsonSchema[None]=None

class MessageIndex(BaseModel):
    index: str

class UidMarketplace(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})
    marketplace: ObjectId
    uid: str

    @model_validator(mode='before')
    def setMarketplace(cls, data):
        data['marketplace'] = ObjectId(data['marketplace'])
        return data

class AmazonParentReportQueueMessage(MessageIndexOptional, UidMarketplace):
    step: AmazonDailyReportAggregationStep
    date: datetime|SkipJsonSchema[None]=None
    query: Query|SkipJsonSchema[None]=None

class DzgroReportQueueMessage(MessageIndex, UidMarketplace):
    reporttype: DzgroReportType

class PaymentMessage(MessageIndex):
    uid: str
    amount:float
    gst: int
    date: datetime

class UserDetails(BaseModel):
    name: str
    email: str
    phone: str|SkipJsonSchema[None]=None
    userpoolid: str

class NewUserQueueMessage(BaseModel):
    uid: str
    details: UserDetails


MODEL_REGISTRY: dict[str, Type[BaseModel]] = {
    "AmazonParentReportQueueMessage": AmazonParentReportQueueMessage,
    "NewUserQueueMessage": NewUserQueueMessage,
    "DzgroReportQueueMessage": DzgroReportQueueMessage,
    "PaymentMessage": PaymentMessage,
}