from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.enums import AdState

class Audit(BaseModel):
    creationDateTime: str | SkipJsonSchema[None] = None
    lastUpdatedDateTime: str | SkipJsonSchema[None] = None

class MonetaryBudget(BaseModel):
    amount: float | SkipJsonSchema[None] = None
    currencyCode: str | SkipJsonSchema[None] = None

class BudgetCap(BaseModel):
    monetaryBudget: MonetaryBudget | SkipJsonSchema[None] = None

class Budget(BaseModel):
    budgetCap: BudgetCap | SkipJsonSchema[None] = None


class CampaignDataSet(BaseModel):
    campaignId: str
    portfolioId: str | SkipJsonSchema[None] = None
    name: str
    state: AdState
    budget: Budget
    audit: Audit

    @model_validator(mode="after")
    def validate_portfolioId(self):
        if self.portfolioId:
            self.portfolioId = None if not self.portfolioId.strip() else self.portfolioId
        return self

class DefaultBid(BaseModel):
    value: float

class AdGroupBidValue(BaseModel):
    defaultBid: DefaultBid

class AdGroupDataSet(BaseModel):
    adGroupId: str
    name: str
    state: AdState
    bidValue: AdGroupBidValue | SkipJsonSchema[None] = None
    audit: Audit

class AdDataSet(BaseModel):
    adId: str
    name: str | SkipJsonSchema[None] = None
    state: AdState
    audit: Audit

class TargetDataSet(BaseModel):
    targetId: str
    bid: float
    state: AdState
    audit: Audit
