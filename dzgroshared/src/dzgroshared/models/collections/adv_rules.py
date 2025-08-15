


from enum import Enum
from dzgroshared.models.collections.country_details import BidMinMax
from dzgroshared.models.enums import AdAssetType, AdProduct, Operator
from dzgroshared.models.model import ItemId, LabelValue
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema

class AdCriteriaResultAction(str, Enum):
    PAUSE_TARGET = "Pause Target"
    SET_BID = "Set Bid"
    UPDATE_BID = "Update Bid"
    CREATE_TARGET = "Create Target"
    ADD_NEGATIVE_TARGET = "Mark Negative"

class AdCriteriaResultSubAction(str, Enum):
    CALCULATED = "CPC * Target Acos/Actual Acos"
    INCREASE_PERCENT = "Increase %"
    DECREASE_PERCENT = "Decrease %"
    SET_KEYWORD_BID = "Set as Keyword Bid"
    SET_CPC_BID = "Set CPC as Bid"
    SET_EXACT_BID = "Set Exact Bid"

class AdCriteriaResultSubActionLabel(str, Enum):
    CALCULATED = "Target Acos"
    INCREASE_PERCENT = "Set % Increase"
    DECREASE_PERCENT = "Set % Decrease"
    SET_EXACT_BID = "Bid Value"


class AdRuleFilter(str, Enum):
    CAMPAIGNS = "Campaigns"
    AD_GROUPS = "Ad Groups"

    @staticmethod
    def values():
        return list(map(lambda c: c, AdRuleFilter))

class AdKey(str, Enum):
    Impressions = "impressions"
    Clicks = "clicks"
    CTR = "ctr"
    Orders = "orders"
    Units = "units"
    Sales = "sales"
    Spend = "cost"
    CPC = "cpc"
    CVR = "cvr"
    ACoS = "acos"
    RoAS = "roas"

    @staticmethod
    def values():
        return list(map(lambda c: c, AdKey))

    @staticmethod
    def names():
        return list(map(lambda c: c.name, AdKey))

    @staticmethod
    def labelValues():
        return list(map(lambda c: LabelValue(label=c.name, value=c.value), AdKey))

class AdCriteriaGroupSubActions(BaseModel):
    action: AdCriteriaResultSubAction
    label: AdCriteriaResultSubActionLabel
    currency: bool|SkipJsonSchema[None] = None
    suffix: str|SkipJsonSchema[None] = None

    
class AdCriteriaGroup(BaseModel):
    action: AdCriteriaResultAction
    subactions: list[AdCriteriaGroupSubActions]|SkipJsonSchema[None] = None

class AdCriteriaParams(BaseModel):
    keys: list[LabelValue]
    criteriaGroups: list[AdCriteriaGroup]
    bids: BidMinMax
    operators: list[LabelValue]
    currency: str
class AdRuleCondition(BaseModel):
    metric: AdKey
    operator: Operator
    val: float


class AdCriteriaResult(BaseModel):
    action: AdCriteriaResultAction
    subaction: AdCriteriaResultSubAction|SkipJsonSchema[None]=None
    label: AdCriteriaResultSubActionLabel|SkipJsonSchema[None]=None
    val: float|SkipJsonSchema[None]=None

class AdCriteriaSimplifiedList(BaseModel):
    criterias: list[str]
    result: str

class CriteriaConditions(BaseModel):
    conditions: list[AdRuleCondition]

class AdCriteria(CriteriaConditions):
    result: AdCriteriaResult

class SimplifyAdRuleRequest(BaseModel):
    filters: list[AdRuleCondition]
    criterias: list[AdCriteria]

class CreateAdRuleRequest(SimplifyAdRuleRequest):
    name: str
    exclude: int = 0
    lookback: int
    description: str
    assettype: AdAssetType
    adproduct: AdProduct

class AdRuleAssetTypeWithAdProduct(BaseModel):
    assettype: AdAssetType
    adproducts: list[AdProduct]

class CriteriasSimplified(BaseModel):
    conditions: str
    result: str

class AdRuleSummary(BaseModel):
    criterias: list[CriteriasSimplified]
    filters: str

class AdRule(ItemId, CreateAdRuleRequest):
    summary: AdRuleSummary|SkipJsonSchema[None]=None
    isAutomated: bool = False
    running: bool = False
    

    @model_validator(mode="after")
    def setSimplified(self):
        self.summary = getAdRuleSummary(self.criterias, self.filters)
        return self
		

def getAdRuleSummary(criterias: list[AdCriteria], filters: list[AdRuleCondition]):
    def getResult(result: AdCriteriaResult):
        if result.action==AdCriteriaResultAction.PAUSE_TARGET: return AdCriteriaResultAction.PAUSE_TARGET.value
        elif result.subaction==AdCriteriaResultSubAction.CALCULATED: return f'{result.action.value} as {result.subaction.value.replace('CPC', str(result.val)+'%')}'
        elif result.subaction==AdCriteriaResultSubAction.DECREASE_PERCENT: return f'Decrease Bid by ${result.val}%'
        elif result.subaction==AdCriteriaResultSubAction.INCREASE_PERCENT: return f'Increase Bid by ${result.val}%'
        elif result.subaction is not None: return result.subaction.value
        return ''
    
    def getFilter(conditions: list[AdRuleCondition]):
        res = list(map(lambda x: f'{x.metric.name} {next((i['value'] for i in operators if i['label']==x.operator.value),None)} {x.val}', conditions))
        return ' & '.join(res)

    def simplify(criteria: AdCriteria):
        return CriteriasSimplified(conditions=getFilter(criteria.conditions), result=getResult(criteria.result))
    
    operators = Operator.withSigns()
    return AdRuleSummary(criterias=list(map(lambda x: simplify(x), criterias)), filters=getFilter(filters))