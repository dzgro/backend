
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel

# Enums
class EntityState(str, Enum):
    ENABLED = "ENABLED"

class CurrencyCode(str, Enum):
    USD = "USD"
    CAD = "CAD"
    GBP = "GBP"
    EUR = "EUR"
    CNY = "CNY"
    JPY = "JPY"
    INR = "INR"
    MXN = "MXN"
    AUD = "AUD"
    AED = "AED"
    BRL = "BRL"
    SGD = "SGD"
    SEK = "SEK"
    TRY = "TRY"
    SAR = "SAR"
    EGP = "EGP"
    PLN = "PLN"
    CLP = "CLP"
    COP = "COP"
    NGN = "NGN"
    ZAR = "ZAR"

class PolicyType(str, Enum):
    DATE_RANGE = "DATE_RANGE"
    MONTHLY_RECURRING = "MONTHLY_RECURRING"
    NO_CAP = "NO_CAP"
    OTHER = "OTHER"

# Models
class PortfolioBudget(BaseModel):
    amount: Optional[float] = None
    endDate: Optional[str] = None
    currencyCode: CurrencyCode
    startDate: Optional[str] = None
    policy: Optional[PolicyType] = None

class BudgetControls(BaseModel):
    campaignUnspentBudgetSharing: Optional[dict] = None  # FeatureState can be modeled if needed

class PortfolioExtendedData(BaseModel):
    statusReasons: Optional[List[str]] = None
    lastUpdateDateTime: Optional[str] = None
    servingStatus: Optional[str] = None
    creationDateTime: Optional[str] = None

class Portfolio(BaseModel):
    inBudget: Optional[bool] = None
    portfolioId: str
    budgetControls: Optional[BudgetControls] = None
    name: str
    state: EntityState
    budget: Optional[PortfolioBudget] = None
    extendedData: Optional[PortfolioExtendedData] = None

class ListPortfoliosResponseContent(BaseModel):
    totalResults: Optional[int] = None
    nextToken: Optional[str] = None
    portfolios: List[Portfolio]

class CreatePortfolio(BaseModel):
    budgetControls: Optional[BudgetControls] = None
    name: str
    state: EntityState
    budget: Optional[PortfolioBudget] = None

class CreatePortfoliosRequestContent(BaseModel):
    portfolios: List[CreatePortfolio]

class CreatePortfoliosResponseContent(BaseModel):
    portfolios: dict  # BulkPortfolioOperationResponse can be modeled if needed

class UpdatePortfolio(BaseModel):
    portfolioId: str
    budgetControls: Optional[BudgetControls] = None
    name: Optional[str] = None
    state: Optional[EntityState] = None
    budget: Optional[PortfolioBudget] = None

class UpdatePortfoliosRequestContent(BaseModel):
    portfolios: List[UpdatePortfolio]

class UpdatePortfoliosResponseContent(BaseModel):
    portfolios: dict  # BulkPortfolioOperationResponse can be modeled if needed

class BudgetUsagePortfolioRequest(BaseModel):
    portfolioIds: List[str]

class BudgetUsagePortfolio(BaseModel):
    budgetUsagePercent: Optional[float] = None
    portfolioId: str
    usageUpdatedTimestamp: Optional[str] = None
    index: Optional[int] = None
    budget: Optional[float] = None

class BudgetUsagePortfolioResponse(BaseModel):
    success: List[BudgetUsagePortfolio]
    error: Optional[list] = None  # BudgetUsagePortfolioBatchError can be modeled if needed

class ObjectIdFilter(BaseModel):
    include: List[str]

class EntityStateFilter(BaseModel):
    include: List[EntityState]

class NameFilter(BaseModel):
    queryTermMatchType: Optional[str] = None  # Can be an Enum if needed
    include: List[str]

class ListPortfoliosRequestContent(BaseModel):
    portfolioIdFilter: Optional[ObjectIdFilter] = None
    stateFilter: Optional[EntityStateFilter] = None
    nextToken: Optional[str] = None
    includeExtendedDataFields: Optional[bool] = None
    nameFilter: Optional[NameFilter] = None