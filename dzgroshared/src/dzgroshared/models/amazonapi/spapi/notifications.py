from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, RootModel
from dzgroshared.models.model import ErrorDetail

# Enums
class AggregationTimePeriod(str, Enum):
    FIVE_MINUTES = "FiveMinutes"
    TEN_MINUTES = "TenMinutes"

class OrderChangeTypeEnum(str, Enum):
    ORDER_STATUS_CHANGE = "OrderStatusChange"
    BUYER_REQUESTED_CHANGE = "BuyerRequestedChange"

class EventFilterType(str, Enum):
    ANY_OFFER_CHANGED = "ANY_OFFER_CHANGED"
    ORDER_CHANGE = "ORDER_CHANGE"

# Aggregation
class AggregationSettings(BaseModel):
    aggregation_time_period: AggregationTimePeriod = Field(..., alias="aggregationTimePeriod")

class AggregationFilter(BaseModel):
    aggregation_settings: Optional[AggregationSettings] = Field(None, alias="aggregationSettings")

# Marketplace
class MarketplaceFilter(BaseModel):
    marketplace_ids: Optional[List[str]] = Field(None, alias="marketplaceIds")

# Order Change
class OrderChangeTypeFilter(BaseModel):
    order_change_types: Optional[List[OrderChangeTypeEnum]] = Field(None, alias="orderChangeTypes")

# Event Filter
class EventFilter(BaseModel):
    event_filter_type: EventFilterType = Field(..., alias="eventFilterType")
    marketplace_ids: Optional[List[str]] = Field(None, alias="marketplaceIds")
    aggregation_settings: Optional[AggregationSettings] = Field(None, alias="aggregationSettings")
    order_change_types: Optional[List[OrderChangeTypeEnum]] = Field(None, alias="orderChangeTypes")

# Processing Directive
class ProcessingDirective(BaseModel):
    event_filter: Optional[EventFilter] = Field(None, alias="eventFilter")

# SQS Resource
class SqsResource(BaseModel):
    arn: str

# EventBridge Resource
class EventBridgeResourceSpecification(BaseModel):
    region: str
    account_id: str = Field(..., alias="accountId")

class EventBridgeResource(BaseModel):
    name: str
    region: str
    account_id: str = Field(..., alias="accountId")

# Destination Resource
class DestinationResource(BaseModel):
    sqs: Optional[SqsResource] = None
    event_bridge: Optional[EventBridgeResourceSpecification] = Field(None, alias="eventBridge")

class DestinationResourceSpecification(BaseModel):
    sqs: Optional[SqsResource] = None
    event_bridge: Optional[EventBridgeResourceSpecification] = Field(None, alias="eventBridge")

# Destination
class Destination(BaseModel):
    destination_id: str = Field(..., alias="destinationId")
    name: str
    resource: DestinationResource

class DestinationList(RootModel[List[Destination]]):
    pass

# Subscription
class Subscription(BaseModel):
    subscription_id: str = Field(..., alias="subscriptionId")
    payload_version: str = Field(..., alias="payloadVersion")
    destination_id: str = Field(..., alias="destinationId")
    processing_directive: Optional[ProcessingDirective] = Field(None, alias="processingDirective")

# Requests
class CreateDestinationRequest(BaseModel):
    name: str
    resource_specification: DestinationResourceSpecification = Field(..., alias="resourceSpecification")

class CreateSubscriptionRequest(BaseModel):
    payload_version: str = Field(..., alias="payloadVersion")
    destination_id: str = Field(..., alias="destinationId")
    processing_directive: Optional[ProcessingDirective] = Field(None, alias="processingDirective")

# Responses
class CreateDestinationResponse(BaseModel):
    payload: Optional[Destination] = None
    errors: Optional[List[ErrorDetail]] = None

class GetDestinationResponse(BaseModel):
    payload: Optional[Destination] = None
    errors: Optional[List[ErrorDetail]] = None

class GetDestinationsResponse(BaseModel):
    payload: Optional[List[Destination]] = None
    errors: Optional[List[ErrorDetail]] = None

class DeleteDestinationResponse(BaseModel):
    errors: Optional[List[ErrorDetail]] = None

class CreateSubscriptionResponse(BaseModel):
    payload: Optional[Subscription] = None
    errors: Optional[List[ErrorDetail]] = None

class GetSubscriptionResponse(BaseModel):
    payload: Optional[Subscription] = None
    errors: Optional[List[ErrorDetail]] = None

class GetSubscriptionByIdResponse(BaseModel):
    payload: Optional[Subscription] = None
    errors: Optional[List[ErrorDetail]] = None

class DeleteSubscriptionByIdResponse(BaseModel):
    errors: Optional[List[ErrorDetail]] = None 