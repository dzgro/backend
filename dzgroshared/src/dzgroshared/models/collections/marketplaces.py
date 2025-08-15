from pydantic import BaseModel, Field,model_validator
from dzgroshared.models.model import ItemId, ItemIdWithDate
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import AmazonAccountType, MarketplaceId, CountryCode, MarketplaceStatus
from datetime import datetime
from typing import Literal


class NameCountryCode(BaseModel):
    name: str
    countrycode: CountryCode
class Account(ItemId, NameCountryCode):
    sellerid: str|SkipJsonSchema[None]=None

# class SellerSubscriptions(ObjectIdStr):
#     sellerid: str
#     notification: SPAPINotificationType
#     destinationId: str


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

class MarketplaceNameId(ItemId):
    name: str
    
class ComparePeriods(BaseModel):
    curr: list[datetime]
    pre: list[datetime]

class RangeDates(ComparePeriods):
    title: str
    key: str

class DefectsAndViolations(BaseModel):
    title: str
    value: str
    type: Literal['Defect','Violation']
# class MarketplaceListItem(Marketplace):
#     dataAvailabilityPeriod: int|SkipJsonSchema[None]=None
#     lastRefreshed: datetime|SkipJsonSchema[None]=None
#     healthScore: float|SkipJsonSchema[None]=None
#     defectsAndViolations: list[DefectsAndViolations] = []
    # reportUpdate: MarketplaceReportUpdate|SkipJsonSchema[None]=None
class DateRange(BaseModel):
    startDate: datetime
    endDate: datetime
    ranges: list[RangeDates]
    titles: list[dict]


class UserAccountsCount(BaseModel):
    spapiAccountsCount: int
    advertisingAccountsCount: int

class RenameAccountRequest(BaseModel):
    id :str
    accountType: AmazonAccountType
    name: str

class Marketplace(ItemIdWithDate):
    countrycode: CountryCode
    marketplaceid: MarketplaceId
    profileid: int
    status: MarketplaceStatus
    storename: str|SkipJsonSchema[None]=None
    startdate: datetime|SkipJsonSchema[None]=None
    enddate: datetime|SkipJsonSchema[None]=None
