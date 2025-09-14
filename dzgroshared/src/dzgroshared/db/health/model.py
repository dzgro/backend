
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, model_validator

class ReportingDates(BaseModel):
    reportingDateFrom: datetime
    reportingDateTo: datetime

class ReportingDateRange(BaseModel):
    reportingDateRange: ReportingDates

class StatusWithTargets(BaseModel):
    status: str
    targetValue: float
    targetCondition: Literal["LESS_THAN","EQUALS","GREATER_THAN"]

class OrderCountAndRate(BaseModel):
    orderCount: int
    rate: float

class StatusAndCount(BaseModel):
    status: str
    count: int

class LateShipmentRate(ReportingDateRange, StatusWithTargets, OrderCountAndRate):
    lateShipmentCount: int

class InvoiceDefectRate(ReportingDateRange, StatusWithTargets, OrderCountAndRate):
    invoiceDefect: StatusAndCount
    missingInvoice: StatusAndCount
    lateInvoice: StatusAndCount

class OrderDefectRate(ReportingDateRange, StatusWithTargets, OrderCountAndRate):
    orderWithDefects: StatusAndCount
    claims: StatusAndCount
    chargebacks: StatusAndCount
    negativeFeedback: StatusAndCount

class OnTimeDeliveryRate(ReportingDateRange, StatusWithTargets):
    shipmentCountWithValidTracking: int
    onTimeDeliveryCount: int
    rate: float

class ValidTrackingRate(ReportingDateRange, StatusWithTargets):
    shipmentCount: int
    validTrackingCount: int
    rate: float

class PreFulfillmentCancellationRate(ReportingDateRange, StatusWithTargets, OrderCountAndRate):
    cancellationCount: int

class Violations(ReportingDateRange, StatusWithTargets):
    name: str
    defectsCount: int



class AmazonHealthReport(BaseModel):
    status: str
    ahrStatus: str
    ahrScore: int
    lateShipment: LateShipmentRate
    invoiceDefect: InvoiceDefectRate
    afnOrderDefectRate: OrderDefectRate
    mfnOrderDefectRate: OrderDefectRate
    onTimeDeliveryRate: OnTimeDeliveryRate
    validTrackingRate: ValidTrackingRate
    preFulfillmentCancellationRate: PreFulfillmentCancellationRate
    violations: list[Violations]

    
class AHR(BaseModel):
    score: int
    status: str
    baseline: int = 1000

class DefectRateItem(BaseModel):
    title: Literal['Negative Feedback', 'A-Z Claims','Chargeback Claims']
    value: str

class InvoiceDefectRateItem(BaseModel):
    title: Literal['Invoice Defects', 'Missing Invoice','Late Invoice']
    value: str

class ValueTarget(BaseModel):
    value: str
    target: str

class DefectRates(ValueTarget):
    subtitle: str
    days: str = ''
    isAcceptable: bool
    
    
class FulfillmentDefectRates(DefectRates):
    fulfillment: str
    title: str = ''
    description: str = ''
    items: list[DefectRateItem]
    
    @model_validator(mode="after")
    def setDetails(self):
        self.description = "The Order Defect Rate (ODR) is a performance metric that Amazon uses to rate the seller's customer service standards"
        self.title = "Seller" if self.fulfillment == 'mfn' else "Amazon"+" Fulfilled Order Defect Rate"    
        return self
    
class InvoiceDefectRates(DefectRates):
    title: str = ''
    description: str = 'The Invoice Defect Rate (IDR) for Amazon is the percentage of orders from Amazon Business customers with the invoice not uploaded within one business day after shipment'
    items: list[InvoiceDefectRateItem]


class DefectRatesByFulfillment(BaseModel):
    afn: FulfillmentDefectRates
    mfn: FulfillmentDefectRates

class RateMetrics(DefectRates):
    title: Literal['Late Shipment Rate', 'On Time Delivery Rate', 'Pre-fulfillment Cancel Rate', 'Valid Tracking Rate']
    desc: str = ''

    @model_validator(mode="after")
    def setDetails(self):
        if self.title=='Late Shipment Rate':
            self.desc = "Amazon's late shipment rate (LSR) is a metric that measures how many orders a seller ships late. It's calculated by dividing the number of late orders by the total number of orders in a given time period."
        elif self.title=='On Time Delivery Rate':
            self.desc = "Your OTDR includes all shipments which are delivered by their Estimated Delivery Date (EDD) represented as a percentage of total tracked shipments. OTDR only applies to seller-fulfilled orders"
        elif self.title=='Pre-fulfillment Cancel Rate':
            self.desc = "A pre-fulfillment cancellation rate (PCR) is the percentage of orders that a seller cancels before they are shipped. It is calculated by dividing the number of cancellations by the total number of orders placed within a given time period. The reason for the cancellation is not considered in the calculation."
        elif self.title=='Valid Tracking Rate':
            self.desc = "The Valid Tracking Rate (VTR) measures the percentage of seller-fulfilled orders that have a valid tracking number."
        return self

class HealthViolationItem(BaseModel):
    name: str
    value: int

class HealthViolation(BaseModel):
    title: str = 'Violations'
    subtitle: str = 'Click for Details'
    categories: int
    isAcceptable: bool
    value: int
    violations: list[HealthViolationItem]
    
    
class AmazonHealthReportConverted(BaseModel):
    ahr: AHR
    defectRates: DefectRatesByFulfillment
    invoiceDefectRate: InvoiceDefectRates
    rateMetrics: list[RateMetrics]
    violation: HealthViolation


class MarketplaceHealthResponse(BaseModel):
    health: AmazonHealthReportConverted
