from enum import Enum
from dzgroshared.db.model import MarketplaceObjectId, PyObjectId
from dzgroshared.functions.RazorpayWebhookProcessor.models import InvoiceExpiredQM, InvoicePaidQM, OrderPaidQM
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from bson import ObjectId
from dzgroshared.db.enums import AmazonDailyReportAggregationStep, CountryCode, QueueMessageModelType
from typing import Type, Union
from dzgroshared.db.dzgro_reports.model import DzgroReportType

class MessageIndexOptional(BaseModel):
    index: str|SkipJsonSchema[None]=None

class MessageIndex(BaseModel):
    index: str

class AmazoMarketplaceDailyReportQM(MessageIndexOptional, MarketplaceObjectId):
    uid:str
    step: AmazonDailyReportAggregationStep
    date: datetime|SkipJsonSchema[None]=None

class DzgroReportQM(MessageIndex, MarketplaceObjectId):
    uid:str
    reporttype: DzgroReportType

class DailyReportByCountryQM(BaseModel):
    index: CountryCode
    success: int|SkipJsonSchema[None]=None
    failed: int|SkipJsonSchema[None]=None
    total: int|SkipJsonSchema[None]=None

QueueMessageModel = Union[AmazoMarketplaceDailyReportQM, DzgroReportQM, DailyReportByCountryQM, OrderPaidQM, InvoicePaidQM, InvoiceExpiredQM]

MODEL_REGISTRY: dict[QueueMessageModelType, Type[QueueMessageModel]] = {
    QueueMessageModelType.AMAZON_DAILY_REPORT: AmazoMarketplaceDailyReportQM,
    QueueMessageModelType.DZGRO_REPORT: DzgroReportQM,
    QueueMessageModelType.COUNTRY_REPORT: DailyReportByCountryQM,
    QueueMessageModelType.ORDER_PAID: OrderPaidQM,
    QueueMessageModelType.INVOICE_PAID: InvoicePaidQM,
    QueueMessageModelType.INVOICE_EXPIRED: InvoiceExpiredQM,
}
