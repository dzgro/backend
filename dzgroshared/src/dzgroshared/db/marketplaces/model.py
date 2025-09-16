from dzgroshared.amazonapi.model import AmazonApiObject
from dzgroshared.db.health.model import AHR
from dzgroshared.db.pricing.model import OfferType, PricingOffer
from pydantic import BaseModel, Field,model_validator
from dzgroshared.db.model import Count, CountryDetails, ItemId, ItemId, PyObjectId, StartEndDate
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.enums import AmazonAccountType, MarketplaceId, CountryCode, MarketplaceStatus, PlanType
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



class MarketplaceObjectForReport(ItemId):
    uid:str
    status: MarketplaceStatus
    marketplaceid: MarketplaceId
    spapi: AmazonApiObject
    ad: AmazonApiObject
    dates: StartEndDate|SkipJsonSchema[None]=None
    lastrefresh: datetime|SkipJsonSchema[None]=None
    details: CountryDetails
    plantype: PlanType



class UserMarketplaceHealth(BaseModel):
    ahr: AHR
    violations: int

class UserMarketplaceSalesData(BaseModel):
    orders: int
    units: int
    revenue: int
    roas: float

class UserMarketplaceDetails(BaseModel):
    count: int
    countries: list[CountryCode]
    statuses: list[MarketplaceStatus]
    plantypes: list[PlanType]


class SellerMarketplace(BaseModel):
    storename: str
    countrycode: CountryCode
    marketplaceid: MarketplaceId

class UserMarketplaceBasic(SellerMarketplace, ItemId):
    status: MarketplaceStatus
    gstin: PyObjectId|SkipJsonSchema[None]=None

class UserMarketplace(UserMarketplaceBasic):
    createdat: datetime
    seller: str
    dates: StartEndDate|SkipJsonSchema[None]=None
    plantype: PlanType|SkipJsonSchema[None]=None
    health: UserMarketplaceHealth|SkipJsonSchema[None]=None
    sales: UserMarketplaceSalesData|SkipJsonSchema[None]=None
    lastrefresh: datetime|SkipJsonSchema[None]=None

class UserMarketplaceList(BaseModel):
    data: list[UserMarketplace]
    count: int|SkipJsonSchema[None]=None

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

class DateRange(BaseModel):
    startDate: datetime
    endDate: datetime
    ranges: list[RangeDates]
    titles: list[dict]


class UserAccountsCount(BaseModel):
    spapiAccountsCount: int
    advertisingAccountsCount: int

class MarketplaceCache(ItemId):
    countrycode: CountryCode
    marketplaceid: MarketplaceId
    uid: str
    profileid: int
    sellerid: str

class Marketplace(ItemId):
    countrycode: CountryCode
    marketplaceid: MarketplaceId
    profileid: int
    status: MarketplaceStatus
    storename: str
    dates: StartEndDate
    pricing: PyObjectId

class MarketplaceOnboardOffer(ItemId):
    offerType: OfferType
    offer: PricingOffer

class MarketplaceOnboardPaymentRequest(ItemId):
    plantype: PlanType
    pricing: PyObjectId
    offer: MarketplaceOnboardOffer|SkipJsonSchema[None]=None
    

