from dzgroshared.models.enums import DzgroReportType, DzroReportPaymentReconSettlementRangeType
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema
from datetime import datetime
from dzgroshared.models.model import ItemId, ItemIdWithDate, Paginator

class DzgroReportDates(BaseModel):
    startDate: datetime
    endDate: datetime

class DzgroPaymentReconRequest(BaseModel):
    dates: DzgroReportDates
    settlementRange: DzroReportPaymentReconSettlementRangeType
    settlementDate: datetime|SkipJsonSchema[None]=None


class CreateDzgroReportRequest(BaseModel):
    reporttype: DzgroReportType
    orderPaymentRecon: DzgroPaymentReconRequest|SkipJsonSchema[None]=None
    productPaymentRecon: DzgroPaymentReconRequest|SkipJsonSchema[None]=None

class DzgroReport(CreateDzgroReportRequest, ItemIdWithDate):
    messageid: str
    count: int|SkipJsonSchema[None]=None
    key: str|SkipJsonSchema[None]=None
    error: str|SkipJsonSchema[None]=None
    completedat: datetime|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setErrorIfNoData(self):
        if self.count == 0: self.error = "No data found"
        return self


