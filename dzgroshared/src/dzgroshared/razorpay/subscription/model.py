from pydantic import BaseModel,Field,ConfigDict
from pydantic.json_schema import SkipJsonSchema
from typing import Literal
from dzgroshared.razorpay.common import Notes, RazorpayEntity, RazorpayPagination,RazorpayId,ItemObject,snakeCaseToTitleCase
from dzgroshared.db.enums import RazorpaySubscriptionStatus

class SubscriptionDefaults(Notes):
    plan_id: str
    total_count: int
    quantity: int
    start_at: int|SkipJsonSchema[None]=None
    expire_by: int|SkipJsonSchema[None]=None
    customer_notify: int = Field(default=1)
    offer_id: str|SkipJsonSchema[None]=None

class CreateSubscription(SubscriptionDefaults):
    addons: list[ItemObject]|SkipJsonSchema[None]=None

class Subscription(RazorpayId,RazorpayEntity,SubscriptionDefaults):
    model_config = snakeCaseToTitleCase()
    entity: str
    customer_id: str|SkipJsonSchema[None]=None
    status: RazorpaySubscriptionStatus
    current_start: int|SkipJsonSchema[None]=None
    current_end: int|SkipJsonSchema[None]=None
    ended_at: int|SkipJsonSchema[None]=None
    charge_at: int|SkipJsonSchema[None]=None
    end_at: int|SkipJsonSchema[None]=None
    auth_attempts: int|SkipJsonSchema[None]=None
    paid_count: int|SkipJsonSchema[None]=None
    created_at: int
    short_url: str|SkipJsonSchema[None]=None
    has_scheduled_changes: bool|SkipJsonSchema[None]=None
    change_scheduled_at: Literal['now','cycle_end']|SkipJsonSchema[None]=None
    source: str|SkipJsonSchema[None]=None
    remaining_count: int|SkipJsonSchema[None]=None

    def is_usable(self) -> bool:
        return self.status.is_active()

class SubscriptionList(BaseModel):
    items: list[Subscription]
    count: int

class FetchSubscriptions(RazorpayPagination):
    plan_id: str


class UpdateSubscription(RazorpayId):
    plan_id: str
    offer_id: str|SkipJsonSchema[None]=None
    quantity: int = Field(default=1)
    remaining_count: int|SkipJsonSchema[None]=None
    start_at: int
    schedule_change_at: Literal['now','cycle_end']|SkipJsonSchema[None]='now'
    customer_notify: int = Field(default=1)

class AddOfferToSubscription(SubscriptionDefaults):
    pass

class DeleteOfferFromSubscription(BaseModel):
    sub_id: str
    offer_id: str


