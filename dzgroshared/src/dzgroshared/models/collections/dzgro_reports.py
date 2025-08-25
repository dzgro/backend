from dzgroshared.models.enums import DzgroReportType, DzroReportPaymentReconSettlementRangeType
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from dzgroshared.models.model import ItemId, Paginator

reportTypes = [
	{
		"reporttype": DzgroReportType.PAYMENT_RECON,
		"description": ["Order level report with price, tax, expense and net proceeds from settlements","This file also includes additional shipping, giftwrap and discounts"],
		"maxdays": 31
	},
	{
		"reporttype": DzgroReportType.PROFITABILITY,
		"description": ["Profitability Report at Category, Parent, Asin or Sku level", "Report is generated for the specified dates"],
		"maxdays": 31,
        "comingsoon": True
	},
	{
		"reporttype": DzgroReportType.INVENTORY_PLANNING,
		"description": ["Sku level report for inventory levels", "Includes Skus where inventory could be over within defined days", "Based on Last 30 days of Sales"],
	},
	{
		"reporttype": DzgroReportType.OUT_OF_STOCK,
		"description": ["Sku level report for all products with zero inventory"],
	},
]


class DzgroReportDates(BaseModel):
    startdate: datetime|SkipJsonSchema[None]=None
    enddate: datetime|SkipJsonSchema[None]=None

class DzroReportPaymentReconRequest(BaseModel):
    dates: DzgroReportDates
    settlementRange: DzroReportPaymentReconSettlementRangeType
    settlementDate: datetime|SkipJsonSchema[None]=None
    includeExpenseTypes: bool
    includeProducts: bool


class CreateDzgroReportRequest(BaseModel):
    reporttype: DzgroReportType
    paymentrecon: DzroReportPaymentReconRequest|SkipJsonSchema[None]=None

class DzgroReport(CreateDzgroReportRequest, ItemId):
    requested: datetime
    messageid: str
    count: int|SkipJsonSchema[None]=None
    url: str|SkipJsonSchema[None]=None
    error: str|SkipJsonSchema[None]=None

class ListDzgroReportsRequest(BaseModel):
    reporttype: DzgroReportType|SkipJsonSchema[None]=None
    paginator: Paginator

class AvailableDzgroReport(BaseModel):
    reporttype: DzgroReportType
    description: list[str]
    maxdays: int|SkipJsonSchema[None]=None
    comingsoon: bool = False


