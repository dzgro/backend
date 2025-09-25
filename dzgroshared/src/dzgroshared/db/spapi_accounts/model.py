
from typing import List
from dzgroshared.db.marketplaces.model import SellerMarketplace
from dzgroshared.db.model import Count, ItemId
from pydantic import BaseModel
from datetime import datetime
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.enums import CountryCode, AmazonAccountType

class SPAPIAccountRequest(BaseModel):
    code: str
    state: str
    sellerid: str

class SPAPIAccountUrlResponse(BaseModel):
    url: str

class SPAPIAccount(ItemId):
    name: str
    createdat: datetime
    countrycode: CountryCode
    sellerid: str
    accounttype: AmazonAccountType = AmazonAccountType.SPAPI
    
class SPAPIAccountList(BaseModel):
    data: List[SPAPIAccount]

class MarketplaceParticipations(BaseModel):
    data: list[SellerMarketplace]

