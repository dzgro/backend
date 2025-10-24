from dzgroshared.amazonapi.model import AmazonApiObject
from dzgroshared.db.health.model import AHR
from dzgroshared.db.performance_period_results.model import PerformancePeriodGroup
from dzgroshared.db.performance_periods.model import PerformancePeriod
from dzgroshared.db.state_analytics.model import StateMonthDataResponse, StateMonthDataResponseItem
from pydantic import BaseModel, Field,model_validator
from dzgroshared.db.model import Count, CountryDetails, DashboardKeyMetricGroup, ItemId, ItemId, MarketplacePlan, Month, PeriodDataResponse, PyObjectId, StartEndDate
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.enums import AmazonAccountType, CollateType, CurrencyCode, MarketplaceId, CountryCode, MarketplaceStatus, PlanName
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
    plan: MarketplacePlan



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
    plantypes: list[PlanName]


class SellerMarketplace(BaseModel):
    storename: str
    countrycode: CountryCode
    marketplaceid: MarketplaceId

class UserMarketplaceBasic(SellerMarketplace, ItemId):
    status: MarketplaceStatus
    gstin: PyObjectId|SkipJsonSchema[None]=None

class UserMarketplace(UserMarketplaceBasic):
    createdat: datetime
    country: str
    currency: CurrencyCode
    settlementdate: datetime|SkipJsonSchema[None]=None
    seller: str|SkipJsonSchema[None]=None
    dates: StartEndDate|SkipJsonSchema[None]=None
    plan: MarketplacePlan|SkipJsonSchema[None]=None
    health: UserMarketplaceHealth|SkipJsonSchema[None]=None
    sales: UserMarketplaceSalesData|SkipJsonSchema[None]=None
    lastrefresh: datetime|SkipJsonSchema[None]=None

class UserMarketplaceList(BaseModel):
    data: list[UserMarketplace]

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
    dates: StartEndDate|SkipJsonSchema[None]=None
    plantype: PlanName|SkipJsonSchema[None]=None

class Marketplace(ItemId):
    countrycode: CountryCode
    marketplaceid: MarketplaceId
    profileid: int
    status: MarketplaceStatus
    storename: str
    dates: StartEndDate
    pricing: PyObjectId

class DetailedMarketplaceWithData(ItemId):
    storename: str
    marketplaceid: MarketplaceId
    dates: StartEndDate
    lastrefresh: datetime|SkipJsonSchema[None]=None
    details: CountryDetails
    plantype: PlanName
    periods: list[PerformancePeriod]
    months: list[Month]


