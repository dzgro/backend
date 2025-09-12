from dzgroshared.models.amazonapi.spapi.listings import OfferType
from dzgroshared.models.collections.health import AHR
from dzgroshared.models.collections.pricing import PricingOffer
from pydantic import BaseModel, Field,model_validator
from dzgroshared.models.model import Count, ItemId, ItemId, PyObjectId, StartEndDate
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import AmazonAccountType, MarketplaceId, CountryCode, MarketplaceStatus, PlanType
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

class UserMarketplaceBasic(ItemId):
    countrycode: CountryCode
    status: MarketplaceStatus
    storename: str
    gstin: PyObjectId|SkipJsonSchema[None]=None
    marketplaceid: MarketplaceId

class UserMarketplace(UserMarketplaceBasic):
    createdat: datetime
    seller: str
    status: MarketplaceStatus
    dates: StartEndDate
    plantype: PlanType
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
    storename: str|SkipJsonSchema[None]=None
    dates: StartEndDate

class MarketplaceOnboardOffer(ItemId):
    offerType: OfferType
    offer: PricingOffer

class MarketplaceOnboardPaymentRequest(ItemId):
    planid: str
    offer: MarketplaceOnboardOffer|SkipJsonSchema[None]=None
    

