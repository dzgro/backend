from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ParticipationStatus(str, Enum):
    PARTICIPATING = "PARTICIPATING"
    NOT_PARTICIPATING = "NOT_PARTICIPATING"

class MarketplaceParticipation(BaseModel):
    is_participating: bool = Field(..., alias="isParticipating")
    has_suspended_listings: bool = Field(..., alias="hasSuspendedListings")

class MarketplaceParticipationDetail(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    country_code: str = Field(..., alias="countryCode")
    default_currency_code: str = Field(..., alias="defaultCurrencyCode")
    default_language_code: str = Field(..., alias="defaultLanguageCode")
    domain_name: str = Field(..., alias="domainName")
    

class MarketplaceItem(BaseModel):
    marketplace: MarketplaceParticipationDetail = Field(..., alias="marketplace")
    participation: MarketplaceParticipation = Field(..., alias="participation")
    store_name: str = Field(..., alias="storeName")

class GetMarketplaceParticipationsResponse(BaseModel):
    payload: Optional[List[MarketplaceItem]] = None
    errors: Optional[List[dict]] = None 