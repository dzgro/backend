from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from enum import Enum
from models.model import ItemId, Paginator

reportTypes = [
	{
		"reporttype": "Payment Reconciliation",
		"description": ["Order level report with price, tax, expense and net proceeds from settlements","This file also includes additional shipping, giftwrap and discounts"],
		"maxdays": 31
	},
	{
		"reporttype": "Profitability",
		"description": ["Profitability Report at Category, Parent, Asin or Sku level", "Report is generated for the specified dates"],
		"maxdays": 31,
        "comingsoon": True
	},
	{
		"reporttype": "Inventory Planning",
		"description": ["Sku level report for inventory levels", "Includes Skus where inventory could be over within defined days", "Based on Last 30 days of Sales"],
	},
	{
		"reporttype": "Stock Out Skus",
		"description": ["Sku level report for all products with zero inventory"],
	},
]

class DzgroReportType(str, Enum):
    PAYMENT_RECON = "Payment Reconciliation"
    PROFITABILITY = "Profitability"
    INVENTORY_PLANNING = "Inventory Planning"
    OUT_OF_STOCK = "Stock Out Skus"

class CreateDzgroReportRequest(BaseModel):
    reporttype: DzgroReportType
    startdate: datetime|SkipJsonSchema[None]=None
    enddate: datetime|SkipJsonSchema[None]=None

class DzgroReport(CreateDzgroReportRequest, ItemId):
    requested: datetime
    messageid: str
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


