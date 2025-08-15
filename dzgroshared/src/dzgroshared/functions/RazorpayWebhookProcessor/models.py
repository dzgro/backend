from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Dict, Any, List, Literal
from enum import Enum
from pydantic.json_schema import SkipJsonSchema


# --- Enums ---

class SubscriptionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    PENDING = "pending"
    HALTED = "halted"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    CREATED = "created"
    CAPTURED = "captured"
    FAILED = "failed"


class InvoiceStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    CANCELLED = "cancelled"


# --- Entities ---

class SubscriptionEntity(BaseModel):
    id: str
    entity: Literal["subscription"]
    plan_id: str
    status: SubscriptionStatus
    quantity: int
    start_at: int
    auth_attempts: int
    total_count: int
    paid_count: int
    customer_notify: int
    created_at: int
    has_scheduled_changes: bool
    customer_id: str|SkipJsonSchema[None]=None
    notes: dict[str,str]|SkipJsonSchema[None]=None


class PaymentEntity(BaseModel):
    id: str
    entity: Literal["payment"]
    amount: int
    currency: str
    status: PaymentStatus
    method: str
    amount_refunded: int
    captured: bool
    created_at: int
    notes: dict[str,str]|SkipJsonSchema[None]=None


class InvoiceEntity(BaseModel):
    id: str
    entity: Literal["invoice"]
    customer_id: str
    invoice_number: str
    status: InvoiceStatus
    amount: int
    currency: str
    date: int
    created_at: int


# --- Payload Wrapper ---

class RazorpayPayloadBody(BaseModel):
    subscription: Optional[Dict[str, SubscriptionEntity]] = None
    payment: Optional[Dict[str, PaymentEntity]] = None
    invoice: Optional[Dict[str, InvoiceEntity]] = None

    @model_validator(mode="after")
    def validate_known_keys(self) -> "RazorpayPayloadBody":
        known_keys = {"subscription", "payment", "invoice"}
        unknown_keys = set(self.__dict__.keys()) - known_keys
        if unknown_keys:
            raise ValueError(f"Unknown keys in payload: {unknown_keys}")
        return self

    @field_validator("subscription", "payment", "invoice", mode="before")
    @classmethod
    def check_entity_dict(cls, v, field):
        if v is None:
            return v
        if not isinstance(v, dict) or "entity" not in v:
            raise ValueError(f"{field.name} must be a dict with an 'entity' key")
        return v


# --- Full Webhook Payload ---

class RazorpayWebhookPayload(BaseModel):
    entity: str
    account_id: str
    event: str
    contains: List[str]
    payload: RazorpayPayloadBody
    created_at: int
    subscription: SubscriptionEntity|SkipJsonSchema[None]=None
    payment: PaymentEntity|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setValues(self):
        if self.payload.subscription: self.subscription=self.payload.subscription['entity']
        if self.payload.payment: self.payment=self.payload.payment['entity']
        return self


class BusinessClass(str, Enum):
    PERSONAL = 'Personal'
    BUSINESS = 'Business'


class GSTDetails(BaseModel):
    gstin: str
    name: str
    addressline1: str
    addressline2: str
    addressline3: str
    pincode: str
    city: str
    state: str

class BusinessDetails(BaseModel):
    businesstype: BusinessClass|SkipJsonSchema[None]=None
    business: GSTDetails|SkipJsonSchema[None]=None