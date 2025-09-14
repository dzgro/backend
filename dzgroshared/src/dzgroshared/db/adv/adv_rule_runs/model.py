


from datetime import datetime
from typing import Literal
from dzgroshared.db.adv.adv_assets.model import AdAssetTarget
from dzgroshared.db.adv.adv_rules.model import AdKey, AdRule
from dzgroshared.db.enums import AdAssetType
from dzgroshared.db.model import ItemId, LabelValue, MarketplaceObjectId, PyObjectId
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from enum import Enum

class AdRuleRunStatus(str, Enum):
    PROCESSING = "Processing"
    QUEUED = "Queued"
    COMPLETED = "Completed"
    FAILED = "Failed"
    NO_RESULT = "No Results"
    
class RuleAvailableFilters(BaseModel):
    id: str
    name: str

class AdRuleRunFilters(BaseModel):
    filter: AdAssetType
    filterIds: list[str]

class AdRuleRunRequest(BaseModel):
    ruleid: str
    filters: AdRuleRunFilters|SkipJsonSchema[None]=None

class AdRuleRun(ItemId, MarketplaceObjectId):
    ruleId: PyObjectId
    startedat: int
    filters: AdRuleRunFilters|SkipJsonSchema[None]=None
    filterTag: str|SkipJsonSchema[None] = None
    completedat: int|SkipJsonSchema[None]=None
    count: int|SkipJsonSchema[None]=None
    executing: bool|SkipJsonSchema[None]=None
    status: AdRuleRunStatus
    error: str|SkipJsonSchema[None]=None
    discardedIds: list[str] = []

    @model_validator(mode="after")
    def setValues(self):
        if self.filters and len(self.filters.filterIds)==0: self.filters = None
        if self.filters: self.filterTag = f'{len(self.filters.filterIds)} {self.filters.filter.title()}s'
        else: self.filterTag = "No Filters"
        return self

class AdRuleWithRunDetails(BaseModel):
    rule: AdRule
    runHistory: AdRuleRun



class AdRunResultCase(BaseModel):
    simplifiedAction: str
    action: str
    bid: float|SkipJsonSchema[None]=None

class AdRuleRunResult(ItemId):
    ad: dict[AdKey, dict]
    assettype: AdAssetType
    asset: AdAssetTarget|SkipJsonSchema[None]=None
    case: AdRunResultCase

class AdRuleRunResultParams(BaseModel):
    columns: list[LabelValue]
    headers: list[LabelValue] = []
    count: int
    rule: AdRule

    @model_validator(mode="after")
    def setColumns(self):
        if self.rule.assettype==AdAssetType.TARGET:
            self.headers = [LabelValue(label="Target", value="target"), LabelValue(label="Performance", value="ad")]
            self.headers.extend([LabelValue(label="Action", value="simplifiedAction"),LabelValue(label="Current Bid", value="currbid"),LabelValue(label="New Bid", value="bid"),LabelValue(label="Delete", value="delete")])
        return self