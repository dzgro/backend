from typing import Literal
from dzgroshared.db.daily_report_group.model import MarketplaceObjectForReport
from dzgroshared.db.health.model import AmazonHealthReport, AmazonHealthReportConverted, AHR, DefectRateItem, DefectRatesByFulfillment, FulfillmentDefectRates, InvoiceDefectRate, InvoiceDefectRates, InvoiceDefectRateItem, OnTimeDeliveryRate, OrderDefectRate, PreFulfillmentCancellationRate, RateMetrics, HealthViolationItem, HealthViolation, LateShipmentRate, ReportingDates, ValidTrackingRate, Violations
valueError = ValueError("Error in Seller Performance Report")

class HealthReportConvertor:
    marketplace: MarketplaceObjectForReport

    marketplace: MarketplaceObjectForReport
    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace

    def convertToReport(self,data: dict):
        statusDict = next((x for x in data['accountStatuses'] if x["marketplaceId"]==self.marketplace.marketplaceid.value), {})
        status = statusDict['status']
        ahrScore = data['performanceMetrics'][0]['accountHealthRating']['ahrScore']
        ahrStatus = data['performanceMetrics'][0]['accountHealthRating']['ahrStatus']
        lateShipment = LateShipmentRate(**data['performanceMetrics'][0]['lateShipmentRate'])
        invoiceDefect = InvoiceDefectRate(**data['performanceMetrics'][0]['invoiceDefectRate'])
        afnOrderDefectRate = OrderDefectRate(**data['performanceMetrics'][0]['orderDefectRate']['afn'])
        mfnOrderDefectRate = OrderDefectRate(**data['performanceMetrics'][0]['orderDefectRate']['mfn'])
        onTimeDeliveryRate = OnTimeDeliveryRate(**data['performanceMetrics'][0]['onTimeDeliveryRate'])
        validTrackingRate = ValidTrackingRate(**data['performanceMetrics'][0]['validTrackingRate'])
        preFulfillmentCancellationRate = PreFulfillmentCancellationRate(**data['performanceMetrics'][0]['preFulfillmentCancellationRate'])
        violations: list[Violations] = []
        for key, value in data['performanceMetrics'][0].items():
            if key=='listingPolicyViolations':
                value['name'] = "Listing Policy Violations"
                violations.append(Violations(**value))
            elif key=='productAuthenticityCustomerComplaints':
                value['name'] = "Product Authenticity Customer Complaints"
                violations.append(Violations(**value))
            elif key=='productConditionCustomerComplaints':
                value['name'] = "Product Condition Customer Complaints"
                violations.append(Violations(**value))
            elif key=='productSafetyCustomerComplaints':
                value['name'] = "Product Safety Customer Complaints"
                violations.append(Violations(**value))
            elif key=='receivedIntellectualPropertyComplaints':
                value['name'] = "IP Complaints"
                violations.append(Violations(**value))
            elif key=='restrictedProductPolicyViolations':
                value['name'] = "Restricted Product Policy Complaints"
                violations.append(Violations(**value))
            elif key=='suspectedIntellectualPropertyViolations':
                value['name'] = "Suspected IP Violations"
                violations.append(Violations(**value))
            elif key=='foodAndProductSafetyIssues':
                value['name'] = "Food & Safety Issues"
                violations.append(Violations(**value))
            elif key=='customerProductReviewsPolicyViolations':
                value['name'] = "Customer Product Reviews Violations"
                violations.append(Violations(**value))
            elif key=='otherPolicyViolations':
                value['name'] = "Other Policy Violations"
                violations.append(Violations(**value))
            elif key=='documentRequests':
                value['name'] = "Document Requests"
                violations.append(Violations(**value))
        report = AmazonHealthReport(status=status, ahrScore=ahrScore, ahrStatus=ahrStatus, afnOrderDefectRate=afnOrderDefectRate, mfnOrderDefectRate=mfnOrderDefectRate, lateShipment=lateShipment,invoiceDefect=invoiceDefect, onTimeDeliveryRate=onTimeDeliveryRate, validTrackingRate=validTrackingRate, preFulfillmentCancellationRate=preFulfillmentCancellationRate,violations=violations)
        return convertForDashboard(report)


def getRateMetrics(report: AmazonHealthReport):
    lsr = getRateMetric(report.lateShipment.status, 'Late Shipment Rate',report.lateShipment.lateShipmentCount, report.lateShipment.orderCount, report.lateShipment.reportingDateRange, report.lateShipment.targetCondition, report.lateShipment.targetValue, report.lateShipment.rate)
    otdr = getRateMetric(report.onTimeDeliveryRate.status, 'On Time Delivery Rate',report.onTimeDeliveryRate.onTimeDeliveryCount, report.onTimeDeliveryRate.shipmentCountWithValidTracking, report.onTimeDeliveryRate.reportingDateRange, report.onTimeDeliveryRate.targetCondition, report.onTimeDeliveryRate.targetValue, report.onTimeDeliveryRate.rate)
    pfcr = getRateMetric(report.preFulfillmentCancellationRate.status, 'Pre-fulfillment Cancel Rate',report.preFulfillmentCancellationRate.cancellationCount, report.preFulfillmentCancellationRate.orderCount, report.preFulfillmentCancellationRate.reportingDateRange, report.preFulfillmentCancellationRate.targetCondition, report.preFulfillmentCancellationRate.targetValue, report.preFulfillmentCancellationRate.rate)
    vtr = getRateMetric(report.validTrackingRate.status, 'Valid Tracking Rate',report.validTrackingRate.validTrackingCount, report.validTrackingRate.shipmentCount, report.validTrackingRate.reportingDateRange, report.validTrackingRate.targetCondition, report.validTrackingRate.targetValue, report.validTrackingRate.rate)
    return [lsr, pfcr, otdr, vtr]

def getRateMetric(status: str, title: Literal['Late Shipment Rate', 'On Time Delivery Rate', 'Pre-fulfillment Cancel Rate', 'Valid Tracking Rate'], count: int, orderCount: int, reportingDateRange: ReportingDates, targetCondition: str, targetValue: float, rate: float):
    return RateMetrics(
        title=title,
        days = str((reportingDateRange.reportingDateTo-reportingDateRange.reportingDateFrom).days+1)+' days',
        subtitle=str(count)+' of '+str(orderCount)+' orders',
        target=getTarget(targetCondition, targetValue),
        value=str(round(rate*100,1))+'%',
        isAcceptable=status=="GOOD"
        )

def convertOrderDefectRate(dr: OrderDefectRate, fulfillment: str):
    subtitle = 'No Orders'
    value = '-'
    target=getTarget(dr.targetCondition, dr.targetValue)
    days = str((dr.reportingDateRange.reportingDateTo-dr.reportingDateRange.reportingDateFrom).days+1) + 'days'
    if dr.orderCount>0:
        subtitle = f'{dr.orderWithDefects.count} of {dr.orderCount} orders'
        value=f'{round(dr.rate*100,1)}%'
    items: list[DefectRateItem] = [
        DefectRateItem(title='Negative Feedback', value=f'{dr.negativeFeedback.count} Orders' if dr.negativeFeedback.count>0 else '-'),
        DefectRateItem(title='A-Z Claims', value=f'{dr.claims.count} Orders' if dr.claims.count>0 else '-'),
        DefectRateItem(title='Chargeback Claims', value=f'{dr.chargebacks.count} Orders' if dr.chargebacks.count>0 else '-'),
    ]
    return FulfillmentDefectRates(fulfillment=fulfillment, days=days, subtitle=subtitle,target=target ,value=value, items=items, isAcceptable=dr.status=="GOOD" )

def convertInvoiceDefectRate(dr: InvoiceDefectRate):
    subtitle = 'No Orders'
    value = '-'
    target=getTarget(dr.targetCondition, dr.targetValue)
    days = str((dr.reportingDateRange.reportingDateTo-dr.reportingDateRange.reportingDateFrom).days+1) + 'days'
    if dr.orderCount>0:
        subtitle = f'{dr.orderCount} orders in {(dr.reportingDateRange.reportingDateTo-dr.reportingDateRange.reportingDateFrom).days+1} days'
        value=f'{round(dr.rate*100,1)}%'
    items: list[InvoiceDefectRateItem] = [
        InvoiceDefectRateItem(title='Invoice Defects', value=f'{dr.invoiceDefect.count} Orders' if dr.invoiceDefect.count>0 else '-'),
        InvoiceDefectRateItem(title='Missing Invoice', value=f'{dr.missingInvoice.count} Orders' if dr.missingInvoice.count>0 else '-'),
        InvoiceDefectRateItem(title='Late Invoice', value=f'{dr.lateInvoice.count} Orders' if dr.lateInvoice.count>0 else '-'),
    ]
    return InvoiceDefectRates(title='Invoice Defect Rate', days=days, subtitle=subtitle,target=target ,value=value, items=items, isAcceptable=dr.status=="GOOD" )

def getTarget(targetCondition: str, targetValue: float):
    prefix = '>' if targetCondition=='GREATER_THAN' else '<' if targetCondition=='LESS_THAN' else ''
    return f'{prefix}{targetValue*100}%'

def convertForDashboard(report: AmazonHealthReport)->AmazonHealthReportConverted:
        ahr = AHR(status=report.ahrStatus, score=report.ahrScore)
        defectRates = DefectRatesByFulfillment(afn=convertOrderDefectRate(report.afnOrderDefectRate, 'afn'), mfn=convertOrderDefectRate(report.mfnOrderDefectRate, 'mfn'))
        invoiceDefectRate = convertInvoiceDefectRate(report.invoiceDefect)
        rateMetrics = getRateMetrics(report)
        violations: list[HealthViolationItem] = list(map(lambda x: HealthViolationItem(name=x.name, value=x.defectsCount), report.violations))
        violations.sort(key = lambda x: x.value, reverse=True)
        from functools import reduce
        totalViolations = reduce(lambda x,y: x+y.value, violations, 0)
        violation = HealthViolation(value=totalViolations, isAcceptable=totalViolations==0, violations=violations, categories = len(list(filter(lambda x: x.value>0, violations))))
        return AmazonHealthReportConverted(ahr=ahr, defectRates=defectRates, invoiceDefectRate=invoiceDefectRate, rateMetrics=rateMetrics, violation=violation)


