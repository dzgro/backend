from dzgroshared.db.enums import CollateType, DzgroReportType, DzroReportPaymentReconSettlementRangeType, DzgroInventoryPlanningRequestConfiguration
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from dzgroshared.db.model import ItemId, ItemId, Paginator

class DzgroReportDates(BaseModel):
    startDate: datetime
    endDate: datetime
    @model_validator(mode="after")
    def validate_dates(self):
        if self.startDate > self.endDate:
            raise ValueError("Start Date must be before or equal to End Date")
        return self

class DzgroPaymentReconRequest(BaseModel):
    dates: DzgroReportDates
    settlementRange: DzroReportPaymentReconSettlementRangeType
    settlementDate: datetime|SkipJsonSchema[None]=None

class DzgroInventoryPlanningRequest(BaseModel):
    configuration: DzgroInventoryPlanningRequestConfiguration
    dates: DzgroReportDates|SkipJsonSchema[None]=None
    days: int|SkipJsonSchema[None]=None
    dayCount: int|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def validateRequest(self):
        if self.configuration == DzgroInventoryPlanningRequestConfiguration.DATES:
            if not self.dates:
                raise ValueError("Start Date and End Date are required")
            self.dayCount = (self.dates.endDate - self.dates.startDate).days + 1
        elif not self.days or self.days == 0:
            raise ValueError("Days must be greater than 0")
        if not self.dayCount: self.dayCount = self.days
        return self
    
class KeyMetricsRequest(BaseModel):
    dates: DzgroReportDates
    collatetype: CollateType

class KeyMetricsWithGrowthRequest(BaseModel):
    currdates: DzgroReportDates
    prevdates: DzgroReportDates
    collatetype: CollateType

class CreateDzgroReportRequest(BaseModel):
    reporttype: DzgroReportType
    orderPaymentRecon: DzgroPaymentReconRequest|SkipJsonSchema[None]=None
    productPaymentRecon: DzgroPaymentReconRequest|SkipJsonSchema[None]=None
    inventoryPlanning: DzgroInventoryPlanningRequest|SkipJsonSchema[None]=None
    keyMetrics: KeyMetricsRequest|SkipJsonSchema[None]=None
    keyMetricsWithGrowth: KeyMetricsWithGrowthRequest|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def validateRequest(self):
        error  = ValueError("Invalid parameters for report")
        if self.reporttype == DzgroReportType.ORDER_PAYMENT_RECON:
            if not self.orderPaymentRecon: raise error
        elif self.reporttype == DzgroReportType.PRODUCT_PAYMENT_RECON:
            if not self.productPaymentRecon: raise error
        elif self.reporttype == DzgroReportType.INVENTORY_PLANNING:
            if not self.inventoryPlanning: raise error
        elif self.reporttype == DzgroReportType.KEY_METRICS:
            if not self.keyMetrics: raise error
        elif self.reporttype == DzgroReportType.KEY_METRICS_WITH_GROWTH:
            if not self.keyMetricsWithGrowth: raise error
        return self

class DzgroReport(CreateDzgroReportRequest, ItemId):
    messageid: str
    createdat: datetime
    count: int|SkipJsonSchema[None]=None
    key: str|SkipJsonSchema[None]=None
    error: str|SkipJsonSchema[None]=None
    completedat: datetime|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setErrorIfNoData(self):
        if self.count == 0: self.error = "No data found"
        return self
    
class ListDzgroReportsResponse(BaseModel):
    data: list[DzgroReport]


