from dzgroshared.db.dzgro_reports.model import DzgroReport, DzgroReportType
from dzgroshared.db.enums import ENVIRONMENT, CollateType
from dzgroshared.sqs.model import SQSRecord
from dzgroshared.db.queue_messages.model import DzgroReportQM
from dzgroshared.client import DzgroSharedClient
from dzgroshared.storage.model import S3Bucket

class DzgroReportProcessor:
    client: DzgroSharedClient
    messageid: str
    message: DzgroReportQM
    report: DzgroReport
    filename: str

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, record: SQSRecord):
        message = DzgroReportQM.model_validate(record.dictBody)
        self.client.setUid(message.uid)
        self.client.setMarketplaceId(message.marketplace)
        self.messageid = record.messageId
        self.message = message
        self.report = await self.client.db.dzgro_reports.getReport(self.message.index)
        if self.report.messageid==self.messageid:
            try:
                await self.client.db.sqs_messages.setMessageAsProcessing(self.messageid)
                try:
                    self.filename = f'{self.message.uid}/{str(self.message.marketplace)}/{self.report.reporttype.name}/{self.message.index}/{self.report.reporttype.value.replace(' ','_')}'
                    count = await self.getCount()
                    if count==0: return await self.client.db.dzgro_reports.addError(self.report.id, "No data found")
                    # elif count<12000 or self.client.secrets.ENV==ENVIRONMENT.DEV: await self.executeHere()
                    else: await self.runFedQuery()
                    await self.client.db.sqs_messages.setMessageAsCompleted(self.messageid)
                    await self.client.db.dzgro_reports_data.deleteReportData(self.report.id)
                except Exception as e:
                    await self.setError(e)
            except Exception as e:
                pass

    def __getattr__(self, item):
        return None
    
    async def setError(self, e: Exception):
        error = e.args[0] if e.args else str(e)
        await self.client.db.sqs_messages.setMessageAsFailed(self.messageid, error)
        await self.client.db.dzgro_reports.addError(self.message.index, error)

    async def getCount(self):
        count = 0
        if self.report.reporttype==DzgroReportType.ORDER_PAYMENT_RECON:
            if not self.report.orderPaymentRecon: raise ValueError("No options provided for Payment Reconciliation Report")
            from dzgroshared.functions.DzgroReports.ReportTypes.PaymentReconciliation import PaymentReconReportCreator
            await PaymentReconReportCreator(self.client, self.report, self.report.orderPaymentRecon).execute()
        elif self.report.reporttype==DzgroReportType.PRODUCT_PAYMENT_RECON:
            if not self.report.productPaymentRecon: raise ValueError("No options provided for Product Payment Reconciliation Report")
            from dzgroshared.functions.DzgroReports.ReportTypes.PaymentReconciliation import PaymentReconReportCreator
            await PaymentReconReportCreator(self.client, self.report, self.report.productPaymentRecon).execute()
        elif self.report.reporttype==DzgroReportType.INVENTORY_PLANNING: 
            if not self.report.inventoryPlanning: raise ValueError("No options provided for Inventory Planning Report")
            from dzgroshared.functions.DzgroReports.ReportTypes.InventoryPlanning import InventoryPlannerReport
            await InventoryPlannerReport(self.client, self.report.id, self.report.inventoryPlanning).execute()
        elif self.report.reporttype==DzgroReportType.OUT_OF_STOCK: 
            from dzgroshared.functions.DzgroReports.ReportTypes.OutOfStock import OutofStockReport
            await OutofStockReport(self.client, self.report.id).execute()
        elif self.report.reporttype==DzgroReportType.KEY_METRICS: 
            if not self.report.keyMetrics: raise ValueError("No options provided for Key Metrics Report")
            from dzgroshared.functions.DzgroReports.ReportTypes.KeyMetrics import KeyMetricsReportCreator
            await KeyMetricsReportCreator(self.client, self.report, self.report.keyMetrics).execute()
        count = await self.client.db.dzgro_reports_data.count(self.report.id)
        await self.client.db.dzgro_reports.addCount(self.report.id, count)
        return count
    
    async def getProjections(self, collatetype: CollateType|None=None):
        if self.report.keyMetrics:
            collatetype = self.report.keyMetrics.collatetype
        return await self.client.db.dzgro_report_types.getProjection(self.report.reporttype, collatetype)

    async def runFedQuery(self):
        projections = await self.getProjections()
        pipeline = self.getPipeline(projections)
        await self.client.fedDb.createReport(self.filename, pipeline, S3Bucket.DZGRO_REPORTS)
        if self.client.secrets.ENV==ENVIRONMENT.DEV:
            await self.triggerLocal()

    def getPipeline(self, projections: dict):
        return [
            {"$match": {"reportid": self.report.id}},
            {"$project": projections},
            {"$project": {"_id": 0}}
        ]

    async def executeHere(self):
        projections = await self.getProjections()
        pipeline = self.getPipeline(projections)
        data = await self.client.db.dzgro_reports_data.db.aggregate(pipeline)
        await self.triggerLocal(data)
        
    async def triggerLocal(self, data: list[dict]|None=None):
        bucket = self.client.storage.getBucketName(bucket=S3Bucket.DZGRO_REPORTS)
        key = f"{self.filename}.csv"
        triggerDict = {"eventName": "ObjectCreated:Put", "s3": {"bucket": {"name": bucket, "arn": ""}, "object": {"key": key, "size": 0}}}
        triggerObj = self.client.storage.getS3TriggerObject(triggerDict)
        print(triggerObj)
        from dzgroshared.functions.DzgroReportsS3Trigger.handler import DzgroReportS3TriggerProcessor
        await DzgroReportS3TriggerProcessor(self.client).execute(triggerObj, data)

    