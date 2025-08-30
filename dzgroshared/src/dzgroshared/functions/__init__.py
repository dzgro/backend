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
        return await AmsChangeProcessor(self.client).execute(self.event)

    @property
    async def ams_performance(self):
        from dzgroshared.functions.AmsPerformance.handler import AmsPerformanceProcessor
        return await AmsPerformanceProcessor(self.client).execute(self.event)

    @property
    async def dzgro_reports(self):
        from dzgroshared.functions.DzgroReports.handler import DzgroReportProcessor
        return await DzgroReportProcessor(self.client).execute(self.event)

    @property
    async def dzgro_reports_s3_trigger(self):
        from dzgroshared.functions.DzgroReportsS3Trigger.handler import DzgroReportS3TriggerProcessor
        return await DzgroReportS3TriggerProcessor(self.client).execute(self.event)

    @property
    async def payment_processor(self):
        from dzgroshared.functions.PaymentProcessor.handler import PaymentProcessor
        return await PaymentProcessor(self.client).execute(self.event)
    
    @property
    async def razorpay_webhook_processor(self):
        from dzgroshared.functions.RazorpayWebhookProcessor.handler import RazorpayWebhookProcessor
        return await RazorpayWebhookProcessor(self.client).execute(self.event)
    
    @property
    async def amazon_daily_report(self):
        from dzgroshared.functions.AmazonDailyReport.handler import AmazonReportManager
        return await AmazonReportManager(self.client).execute(self.event, self.context)
    
    @property
    async def daily_report_refresh(self):
        from dzgroshared.functions.DailyReportRefreshByCountryCode.handler import DailyReportRefreshByCountryCodeProcessor
        return await DailyReportRefreshByCountryCodeProcessor(self.client).execute(self.event)
    
    @property
    async def send_daily_report_refresh_message_to_queue(self):
        from dzgroshared.functions.SendDailyReportRefreshMessage import handler
        return await handler.sendMessage(self.client, self.event, self.context)

    