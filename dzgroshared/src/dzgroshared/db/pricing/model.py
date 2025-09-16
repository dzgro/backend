
from enum import Enum
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from typing import List, Optional
from dzgroshared.db.model import ItemId, PyObjectId
from dzgroshared.db.enums import PlanType

class PlanDetails(BaseModel):
    plantype: PlanType
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

class PlanDuration(str, Enum):
    MONTH = "1 Month"
    QUARTER = "3 Months"
    YEAR = "1 Year"

class OfferType(str, Enum):
    CASHBACK = "cashback"

class PricingOffer(BaseModel):
    duration: PlanDuration
    discount: float

class PricingOffers(BaseModel):
    offerType: OfferType
    offers: List[PricingOffer] = [
        PricingOffer(duration=PlanDuration.MONTH, discount=0),
        PricingOffer(duration=PlanDuration.QUARTER, discount=10),
        PricingOffer(duration=PlanDuration.YEAR, discount=25)
    ]

class PlanWithPricingDetail(BaseModel):
    plantype: PlanType
    total: float
    items: list[PricingDetailItem]

class PricingDetail(BaseModel):
    currency: str
    currencyCode: str
    plans: list[PlanWithPricingDetail]
    groupId: str
    offers: PricingOffers = PricingOffers(offerType=OfferType.CASHBACK)
    
