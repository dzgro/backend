from bson import ObjectId
from dzgroshared.models.collections.dzgro_reports import DzgroReportType
from dzgroshared.models.enums import CollateTypeTag
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.models.collections.queue_messages import DzgroReportQueueMessage
from dzgroshared.functions import FunctionClient
from dzgroshared.models.sqs import SQSEvent

class DzgroReportProcessor:
    fnclient: FunctionClient
    messageid: str
    message: DzgroReportQueueMessage

    def __init__(self, client: FunctionClient):
        self.fnclient = client

    async def execute(self):
        try:
            parsed = SQSEvent.model_validate(self.fnclient.event)
            for record in parsed.Records:
                message = DzgroReportQueueMessage.model_validate(record.dictBody)
                self.fnclient.client.uid = message.uid
                self.fnclient.client.marketplace = message.marketplace
                self.messageid = record.messageId
                self.message = message
                return await self.processReport()
        except Exception as e:
            print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    def __getattr__(self, item):
        return None
    
    async def setMessageAsProcessing(self):
        updated, id = await self.fnclient.client.db.sqs_messages.setMessageAsProcessing(self.messageid)
        return updated==0
    
    async def setError(self, error: str):
        await self.fnclient.client.db.sqs_messages.setMessageAsFailed(self.messageid, error)
        await self.fnclient.client.db.dzgro_reports.addError(self.message.index, error)

    async def processReport(self):
        try:
            
            if await self.setMessageAsProcessing():
                report = await self.fnclient.client.db.dzgro_reports.getReport(self.message.index)
            if report.messageid==self.messageid:
                if report.reporttype==DzgroReportType.PAYMENT_RECON: 
                    orders = self.fnclient.client.db.orders
                    from dzgroshared.functions.DzgroReports.pipelines import PaymentReconciliation
                    pipeline = PaymentReconciliation.pipeline(orders.db.pp, self.message.index)
                    await orders.db.aggregate(pipeline)
                elif report.reporttype==DzgroReportType.INVENTORY_PLANNING: 
                    _queries = self.fnclient.client.db.queries
                    queries = await _queries.getQueries()
                    query = next((q for q in queries if q.tag==CollateTypeTag.DAYS_30), None)
                    if query:
                        query_results = self.fnclient.client.db.query_results
                        from dzgroshared.functions.DzgroReports.pipelines import InventoryPlanning
                        pipeline = InventoryPlanning.pipeline(query_results.db.pp, self.message.index, str(query.id))
                        await query_results.db.aggregate(pipeline)
                    else: await self.setError("No query found for Inventory Planning")
                elif report.reporttype==DzgroReportType.OUT_OF_STOCK: 
                    products = self.fnclient.client.db.products
                    from dzgroshared.functions.DzgroReports.pipelines import OutOfStock
                    pipeline = OutOfStock.pipeline(products.db.pp, self.message.index)
                    await products.db.aggregate(pipeline)
                pipeline = [{"$match": {"reportid": ObjectId(self.message.index)}}]
                filename = f'{self.message.uid}/{str(self.message.marketplace)}/{report.reporttype.name}/{self.message.index}/data'
                self.fnclient.client.fedDb.createReport(filename, pipeline)
        except Exception as e:
            await self.setError(e.args[0] if e.args else str(e))



    