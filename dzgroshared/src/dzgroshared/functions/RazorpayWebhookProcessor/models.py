from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Dict, Any, List, Literal, Union
from pydantic.json_schema import SkipJsonSchema

class Id(BaseModel):
    id: str

class OrderEntity(Id):
    notes: Dict[str,str]

class PaymentEntity(Id):
    amount: int

class InvoiceExpiredEntity(Id):
    order_id: str
    notes: Dict[str,str]

class InvoicePaidEntity(InvoiceExpiredEntity):
    payment_id: str

class InvoicePaidQM(BaseModel):
    order: OrderEntity
    payment: PaymentEntity
    invoice: InvoicePaidEntity

class InvoiceExpiredQM(BaseModel):
    order: OrderEntity
    invoice: InvoiceExpiredEntity

class OrderPaidQM(BaseModel):
    order: OrderEntity
    payment: PaymentEntity

