
from pydantic import BaseModel
from typing import Optional
from dzgroshared.models.model import ItemId
from dzgroshared.models.enums import PlanType

class PlanDetails(BaseModel):
    name: PlanType
    baseprice: int
    variable: Optional[float] = None


class Plan(PlanDetails):
    active: bool


class FeaturePricing(BaseModel):
    included: bool
    price: Optional[str] = None


class FeatureItem(BaseModel):
    label: str
    sublabel: str
    pricing: list[FeaturePricing]


class Feature(BaseModel):
    label: str
    baseprice: Optional[int] = None
    variable: Optional[float] = None
    active: Optional[bool] = None
    items: list[FeatureItem]


class Pricing(ItemId):
    currency: str
    currencyCode: str
    plans: list[Plan]
    features: list[Feature]

class PricingDetailItem(BaseModel):
    label: str
    sublabel: Optional[str] = None
    value: float

class PricingDetail(BaseModel):
    currency: str
    currencyCode: str
    planid: str
    name:str
    groupId: str
    items: list[PricingDetailItem]
    total: float
    
