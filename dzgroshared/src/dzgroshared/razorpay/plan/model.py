from dzgroshared.razorpay.common import Notes,RazorpayId, ItemObject
from pydantic import BaseModel,Field
from pydantic.json_schema import SkipJsonSchema
from typing import Literal

Interval = Literal['daily','weekly','monthly','yearly']

class PlanPeriodAndInterval(ItemObject,Notes):
    period: Interval = Field(..., description="Billing frequency unit")
    interval: int = Field(..., description="Number of billing intervals between charges")

class Plan(PlanPeriodAndInterval, RazorpayId):
    created_at: int

class PlanDetail(PlanPeriodAndInterval):
    name: str
    amount: int
    currency: str
    description: str | SkipJsonSchema[None] = None
    status: Literal['active', 'inactive'] = 'active'
    notes: Notes | None = None

class CreatePlan(PlanPeriodAndInterval):
    item: PlanDetail
    notes: Notes | SkipJsonSchema[None] = None

