from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import LambdaContext

class FunctionClient:
    client: DzgroSharedClient
    event: dict
    context: LambdaContext

    def __init__(self, client: DzgroSharedClient, event: dict, context: LambdaContext) -> None:
        self.client = client
        self.event = event
        self.context = context

    @property
    async def ams_change(self):
        from dzgroshared.functions.AmsChange.handler import AmsChangeProcessor
        return await AmsChangeProcessor(self).execute()

    @property
    async def ams_performance(self):
        from dzgroshared.functions.AmsPerformance.handler import AmsPerformanceProcessor
        return await AmsPerformanceProcessor(self).execute()

    @property
    async def dzgro_reports(self):
        from dzgroshared.functions.DzgroReports.handler import DzgroReportProcessor
        return await DzgroReportProcessor(self).execute()

    @property
    async def dzgro_reports_s3_trigger(self):
        from dzgroshared.functions.DzgroReportsS3Trigger.handler import DzgroReportS3TriggerProcessor
        return await DzgroReportS3TriggerProcessor(self).execute()

    @property
    async def payment_processor(self):
        from dzgroshared.functions.PaymentProcessor.handler import PaymentProcessor
        return await PaymentProcessor(self).execute()
    
    @property
    async def razorpay_webhook_processor(self):
        from dzgroshared.functions.RazorpayWebhookProcessor.handler import RazorpayWebhookProcessor
        return await RazorpayWebhookProcessor(self).execute()
    
    @property
    async def amazon_daily_report(self):
        from dzgroshared.functions.AmazonDailyReport.handler import AmazonReportManager
        return await AmazonReportManager(self).execute()

    