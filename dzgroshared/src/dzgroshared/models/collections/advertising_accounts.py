
from datetime import datetime
from dzgroshared.models.model import ItemId, RefreshToken
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import CountryCode


class AdvertisingAccountRequest(BaseModel):
    code: str


class AdvertisingAccountUrlResponse(BaseModel):
    url: str

class AdvertisingAccountBasic(BaseModel):
    name: str
    countrycode: CountryCode

class AdvertisingccountRequest(RefreshToken, AdvertisingAccountBasic):
    pass
    
class AdvertisingAccount(ItemId, AdvertisingAccountBasic):
    createdat: datetime


class AdvertisingAccountList(BaseModel):
    data: list[AdvertisingAccount]
    count: int|SkipJsonSchema[None] = None


class AdAccount(BaseModel):
    accountname: str
    entityid: str
    countryCode: CountryCode
    profileid: int
    adsaccountid: str


class AdvertisingAccountInfo(BaseModel):
    marketplaceStringId: str
    id: str
    type: str
    name: str
    validPaymentMethod: bool

class AdvertisingProfile(BaseModel):
    profileId: int
    countryCode: str
    currencyCode: str
    timezone: str
    accountInfo: AdvertisingAccountInfo

class AdAccountsList(BaseModel):
    data: list[AdAccount]