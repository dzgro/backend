
from enum import Enum
from dzgroshared.db.enums import CountryCode, CurrencyCode, MarketplaceId, PlanDuration, PlanName, PlanVariableType
from dzgroshared.db.marketplaces.model import UserMarketplace
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from typing import List, Optional
from dzgroshared.db.model import ItemId, MarketplacePlan, PyObjectId

class PaymentPlanPriceByDuration(BaseModel):
    duration: PlanDuration
    price: float
    variableType: PlanVariableType
    variable: float
    variableUnit: int|SkipJsonSchema[None]=None
    
class PaymentPlan(BaseModel):
    name: PlanName
    active: bool
    description: str
    durations: list[PaymentPlanPriceByDuration]
    
    @model_validator(mode="before")
    def addDetails(cls, data):
        if data['name'] == PlanName.PAYMENT_RECONCILIATION.value:
            data['active'] = True
            data['description'] = "Simplify your payment processes with our automated reconciliation tools."
        elif data['name'] == PlanName.ANALYTICS.value:
            data['active'] = True
            data['description'] = "Gain insights into your sales and performance with our comprehensive analytics."
        elif data['name'] == PlanName.ADVERTISING.value:
            data['description'] = "Boost your visibility and sales with our targeted advertising solutions."
            data['active'] = False
        return data
    
class PricingCountryDetails(BaseModel):
    countryCode: CountryCode
    country: str
    currencyCode: CurrencyCode
    currency: str
    
    
class PricingByCountry(PricingCountryDetails, ItemId):
    plans: list[PaymentPlan]
    
class PlanFeatureDetail(BaseModel):
    name: PlanName
    value: str|bool
    
class PlanFeature(BaseModel):
    name: str
    info: str
    details: list[PlanFeatureDetail]
    
class PlanFeatureGroup(BaseModel):
    title: str
    features: List[PlanFeature]

class Pricing(BaseModel):
    data: list[PricingByCountry]
    features: list[PlanFeatureGroup]
    
class PaymentPricingDetailItem(BaseModel):
    label: str
    sublabel: str|SkipJsonSchema[None]=None
    value: float
    
class PaymentPricingDetail(BaseModel):
    name: PlanName
    duration: PlanDuration
    groups: List[PaymentPricingDetailItem]
    total: float
    
class MarketplacePricing(PricingCountryDetails, ItemId):
    storename: str
    marketplaceid: MarketplaceId
    pricingid: PyObjectId
    plan: MarketplacePlan|SkipJsonSchema[None]
    plans: list[PaymentPlan]
    details: list[PaymentPricingDetail]
    features: list[PlanFeatureGroup]
    

    