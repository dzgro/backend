
from typing import List
from dzgroshared.models.amazonapi.spapi.sellers import MarketplaceItem
from dzgroshared.models.collections.country_details import CountriesByRegion
from dzgroshared.models.model import Count, ItemId, RefreshToken
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import CountryCode

class SPAPIAccountRequest(BaseModel):
    code: str
    state: str
    sellerid: str

class SPAPIAccountUrlResponse(BaseModel):
    url: str

class SPAPIAccount(ItemId):
    name: str
    countrycode: CountryCode
    sellerid: str
    
class SPAPIAccountList(Count):
    data: List[SPAPIAccount]
    count: int|SkipJsonSchema[None]

class MarketplaceParticipations(BaseModel):
    data: list[MarketplaceItem]

