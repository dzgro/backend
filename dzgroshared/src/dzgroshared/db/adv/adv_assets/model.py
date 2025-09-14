from datetime import datetime, timedelta
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from enum import Enum
from dzgroshared.db.model import Paginator, Sort, LabelValue
from dzgroshared.db.enums import AdProduct, AdState, Operator, AdAssetType
from typing import Literal, Any, get_args

class BidValue(BaseModel):
    suggestedBid: float = Field(..., description='The suggested bid.', ge=0.0)

class AssetAd(BaseModel):
    asin: str
    image: str

class AdsInAsset(BaseModel):
    products: list[AssetAd]
    count: int|SkipJsonSchema[None] = None

class AdProductType(BaseModel):
    adproduct: AdProduct|SkipJsonSchema[None] = None

class AdPerformanceValues(BaseModel):
    curr: str = '-'
    pre: str = '-'
    growth: str|SkipJsonSchema[None]=None
    growing: bool|SkipJsonSchema[None]=None

class AdAssetPerformance(BaseModel):
    data: dict[str, AdPerformanceValues]|SkipJsonSchema[None] = None
    
class SPTargetDetails(BaseModel):
    matchType: str
    keyword:str|SkipJsonSchema[None] = None
    asin: str|SkipJsonSchema[None] = None
    productResolved: str|SkipJsonSchema[None] = None

    @model_validator(mode="after")
    def setMatchType(self):
        parts = self.matchType.split('_')
        if len(parts)>1: parts = parts[1:]
        self.matchType = ' '.join([x.title() for x in parts])
        return self

class Bid(BaseModel):
    currencyCode: str
    bid: float|SkipJsonSchema[None] = None
    defaultBid: float|SkipJsonSchema[None] = None

    @model_validator(mode="after")
    def setBid(self):
        if not self.bid and self.defaultBid: self.bid = self.defaultBid
        return self

class SuggestedBidAndRange(BaseModel):
    bidValues: list[BidValue]|SkipJsonSchema[None]=None
    suggestedBid: float|SkipJsonSchema[None]=None
    range: str|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setValues(self):
        if self.bidValues and len(self.bidValues)>=3:
            self.suggestedBid = self.bidValues[1].suggestedBid
            self.range = f'{self.bidValues[0].suggestedBid}-{self.bidValues[2].suggestedBid}'
        return self
    

class Tag(BaseModel):
    key: str
    value: str
class PlacementBidAdjustment(BaseModel):
    percentage: int
    placement: str
class Optimization(BaseModel):
    bidStrategy: str|SkipJsonSchema[None]=None
    placementBidAdjustments: list[PlacementBidAdjustment]|SkipJsonSchema[None]=None
class MonetaryBudget(BaseModel):
    currencyCode: str
    amount: int
class BudgetValue(BaseModel):
    monetaryBudget: MonetaryBudget

class BudgetCaps(BaseModel):
    recurrenceTimePeriod: str
    budgetType: str
    budgetValue: BudgetValue


class AdAssetCampaign(AdProductType):
    state: AdState
    id: str
    name: str
    targetingsettings: str|SkipJsonSchema[None]=None
    deliverystatus: str|SkipJsonSchema[None]=None
    budgetcaps: BudgetCaps
    portfolioid: str|SkipJsonSchema[None] = None
    optimization: Optimization|SkipJsonSchema[None] = None

class AdAssetPortfolio(BaseModel):
    state: AdState
    id: str
    name: str
    
class AdAssetAdGroup(AdProductType):
    state: AdState
    id: str
    campaignid: str
    name: str
    bid: Bid|SkipJsonSchema[None]=None
    deliverystatus: str|SkipJsonSchema[None]=None

def setSpMatchType(matchType: str):
    if(matchType=="EXACT"): return 

class AdAssetTargetType(BaseModel):
    targettype: str|SkipJsonSchema[None] = None
    @model_validator(mode="after")
    def setaTrgetType(self):
        if self.targettype is not None:
            parts = self.targettype.split('_')
            if len(parts)>1: parts = parts[1:]
            self.targettype = ' '.join([x.title() for x in parts])
        return self

class AdAssetTargetDetails(BaseModel):
    targetdetails: SPTargetDetails|SkipJsonSchema[None] = None

class AdAssetTarget(AdProductType, AdAssetTargetType, AdAssetTargetDetails):
    state: AdState
    id: str
    adgroupid: str
    campaignid: str
    adgroup: str|SkipJsonSchema[None]=None
    campaign: str|SkipJsonSchema[None]=None
    deliverystatus: str|SkipJsonSchema[None]=None
    bid: Bid|SkipJsonSchema[None] = None
    negative: bool|SkipJsonSchema[None] = None
    targetingsettings: str|SkipJsonSchema[None] = None
    matchtype: str|SkipJsonSchema[None] = None

class AdAssetAd(AdProductType):
    state: AdState
    id: str
    adgroupid: str
    campaignid: str
    deliverystatus: str|SkipJsonSchema[None]=None

class AdAsset(AdAssetPerformance):
    assettype: AdAssetType
    ads: AdsInAsset|SkipJsonSchema[None] = None
    details: AdAssetCampaign|AdAssetAdGroup|AdAssetTarget|AdAssetAd|AdAssetPortfolio

class AdAssetResponse(AdAssetPerformance):
    count: int
    items: list[AdAsset]

class AdBreadcrumb(BaseModel):
    id: Any
    name: str
    type: Literal['portfolio','campaign','adGroup']

class AdValueFilter(BaseModel):
    key:str
    operation: Operator
    val: float

class AdGrowthFilterEnum(str, Enum):
    ALL = "View All"
    GROWING = "View Only Growing"
    DEGROWING = "View Only Degrowing"

class AdGrowthFilter(BaseModel):
    key:str
    val: AdGrowthFilterEnum

class AdQueryDate(BaseModel):
    start: datetime
    end: datetime

class AdQueryDates(BaseModel):
    curr: AdQueryDate
    pre: AdQueryDate

class AdAssetTypeAndParent(BaseModel):
    assetType: AdAssetType
    parent: str|SkipJsonSchema[None] = None
class ListAdAssetRequest(AdAssetTypeAndParent):
    dates: AdQueryDates
    sort: Sort
    paginator: Paginator
    adProducts: list[AdProduct] = []
    states: list[AdState] = []
    valueFilters: list[AdValueFilter] = []
    growthFilters: list[AdGrowthFilter] = []

class AdColumn(LabelValue):
    ispercent: bool|SkipJsonSchema[None]=None


class MinMaxDate(BaseModel):
    start: datetime
    end: datetime    

class ListAdAssetRequestParams(BaseModel):
    querydates: AdQueryDates
    columns: list[AdColumn]
    minmaxDates: MinMaxDate
    growthFilters: list[AdGrowthFilter]
    adProducts: list[LabelValue]
    states: list[LabelValue]

    @model_validator(mode="before")
    def setgrowthFilters(cls, data):
        data['growthFilters'] = [AdGrowthFilter(key=x['value'], val=AdGrowthFilterEnum.ALL).model_dump() for x in data['columns']]
        data['adProducts'] = [LabelValue(label=x.name, value=x.value).model_dump(exclude_none=True) for x in list(AdProduct.values())]
        data['states'] = [LabelValue(label=x.name.title(), value=x.value).model_dump(exclude_none=True) for x in list(AdState.values())]
        return data

