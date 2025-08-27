from bson import ObjectId
from dzgroshared.models.collections.dzgro_reports import DzgroReport, DzgroReportType
from dzgroshared.models.enums import ENVIRONMENT, CollateTypeTag, S3Bucket
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.models.collections.queue_messages import DzgroReportQueueMessage
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.sqs import SQSEvent

class DzgroReportProcessor:
    client: DzgroSharedClient
    messageid: str
    message: DzgroReportQueueMessage
    report: DzgroReport
    filename: str

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event: dict):
        try:
            parsed = SQSEvent.model_validate(event)
            for record in parsed.Records:
                message = DzgroReportQueueMessage.model_validate(record.dictBody)
                self.client.setUid(message.uid)
                self.client.setMarketplace(message.marketplace)
                self.messageid = record.messageId
                self.message = message
                self.report = await self.client.db.dzgro_reports.getReport(self.message.index)
                if self.report.messageid==self.messageid:
                    if await self.setMessageAsProcessing():
                        try:
                            self.filename = f'{self.message.uid}/{str(self.message.marketplace)}/{self.report.reporttype.name}/{self.message.index}/{self.report.reporttype.value.replace(' ','_')}'
                            count, projection = await self.getCountAndProjection()
                            if count==0: 
                                return await self.client.db.dzgro_reports.addError(self.report.id, "No data found")
                            # elif count<2000 or self.client.env==ENVIRONMENT.LOCAL: await self.executeHere(projection)
                            else: await self.runFedQuery(projection)
                            await self.client.db.sqs_messages.setMessageAsCompleted(self.messageid)
                            await self.client.db.dzgro_reports_data.deleteReportData(self.report.id)
                        except Exception as e:
                            await self.setError(e)
                    else: print(f"[WARNING] Message {record.messageId} is already being processed")
                else: print(f"[WARNING] Message {record.messageId} is not for this report")

        except Exception as e:
            print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    def __getattr__(self, item):
        return None
    
    async def setMessageAsProcessing(self):
        updated, id = await self.client.db.sqs_messages.setMessageAsProcessing(self.messageid)
        return updated==1
    
    async def setError(self, e: Exception):
        error = e.args[0] if e.args else str(e)
        await self.client.db.sqs_messages.setMessageAsFailed(self.messageid, error)
        await self.client.db.dzgro_reports.addError(self.message.index, error)

    async def getCountAndProjection(self):
        count = 0
        projections: list[dict] = []
        if self.report.paymentrecon:
            from dzgroshared.functions.DzgroReports.ReportTypes.PaymentReconciliation import PaymentReconReportCreator
            creator = PaymentReconReportCreator(self.client, self.report.id, self.report.paymentrecon)
            count, projections = await creator.execute()
        await self.client.db.dzgro_reports.addCount(self.report.id, count)
        return count, projections

    async def runFedQuery(self, projections: list[dict]):
        pipeline = self.getPipeline(projections)
        res = await self.client.fedDb.createReport(self.filename, pipeline, S3Bucket.DZGRO_REPORTS)
        if self.client.env==ENVIRONMENT.LOCAL:
            await self.triggerLocal()

    def getPipeline(self, projections: list[dict]):
        return [{"$match": {"reportid": self.report.id}}]+projections

    async def executeHere(self, projections: list[dict]):
        data = await self.client.db.dzgro_reports_data.db.aggregate(self.getPipeline(projections))
        await self.triggerLocal(data)
        
    async def triggerLocal(self, data: list[dict]|None=None):
        bucket = self.client.storage.getBucketName(bucket=S3Bucket.DZGRO_REPORTS)
        key = f"{self.filename}.csv"
        triggerObj = {"eventName": "ObjectCreated:Put", "s3": {"bucket": {"name": bucket, "arn": ""}, "object": {"key": key, "size": 0}}}
        from dzgroshared.functions.DzgroReportsS3Trigger.handler import DzgroReportS3TriggerProcessor
        await DzgroReportS3TriggerProcessor(self.client).execute(self.client.storage.getS3TriggerObject(triggerObj), data)

    async def processReport(self):
        try:
            count: int=0
            if await self.setMessageAsProcessing():
                report = await self.client.db.dzgro_reports.getReport(self.message.index)
                if report.paymentrecon: 
                    from dzgroshared.functions.DzgroReports.ReportTypes.PaymentReconciliation import PaymentReconReportCreator
                    count = await PaymentReconReportCreator(self.client, self.report.id, report.paymentrecon).execute()
                elif report.reporttype==DzgroReportType.INVENTORY_PLANNING: 
                    _queries = self.client.db.queries
                    queries = await _queries.getQueries()
                    query = next((q for q in queries if q.tag==CollateTypeTag.DAYS_30), None)
                    if query:
                        query_results = self.client.db.query_results
                        from dzgroshared.functions.DzgroReports.pipelines import InventoryPlanning
                        pipeline = InventoryPlanning.pipeline(query_results.db.pp, self.message.index, str(query.id))
                        await query_results.db.aggregate(pipeline)
                    else: await self.setError("No query found for Inventory Planning")
                elif report.reporttype==DzgroReportType.OUT_OF_STOCK: 
                    products = self.client.db.products
                    from dzgroshared.functions.DzgroReports.pipelines import OutOfStock
                    pipeline = OutOfStock.pipeline(products.db.pp, self.message.index)
                    await products.db.aggregate(pipeline)
                else: return
                if count==0:
                    await self.client.db.dzgro_reports.addError(report.id, "No data found")
                else:
                    pipeline = [{"$match": {"reportid": report.id}}]
                    filename = f'{self.message.uid}/{str(self.message.marketplace)}/{report.reporttype.name}/{self.message.index}/data'
                    await self.client.fedDb.createReport(filename, pipeline, S3Bucket.DZGRO_REPORTS)
                    await self.client.db.dzgro_reports.addCount(report.id, count)
        except Exception as e:
            await self.setError(e.args[0] if e.args else str(e))



    