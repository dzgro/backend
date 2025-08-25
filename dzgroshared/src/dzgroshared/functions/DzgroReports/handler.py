from bson import ObjectId
from dzgroshared.models.collections.dzgro_reports import DzgroReportType
from dzgroshared.models.enums import CollateTypeTag, S3Bucket
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.models.collections.queue_messages import DzgroReportQueueMessage
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.sqs import SQSEvent

class DzgroReportProcessor:
    client: DzgroSharedClient
    messageid: str
    message: DzgroReportQueueMessage

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
                return await self.processReport()
        except Exception as e:
            print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    def __getattr__(self, item):
        return None
    
    async def setMessageAsProcessing(self):
        updated, id = await self.client.db.sqs_messages.setMessageAsProcessing(self.messageid)
        return updated==1
    
    async def setError(self, error: str):
        await self.client.db.sqs_messages.setMessageAsFailed(self.messageid, error)
        await self.client.db.dzgro_reports.addError(self.message.index, error)

    async def processReport(self):
        try:
            count: int=0
            if await self.setMessageAsProcessing():
                report = await self.client.db.dzgro_reports.getReport(self.message.index)
                if report.paymentrecon: 
                    from dzgroshared.functions.DzgroReports.ReportTypes.PaymentReconciliation import PaymentReconReportCreator
                    count = await PaymentReconReportCreator(self.client, report.id, report.paymentrecon).execute()
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



    