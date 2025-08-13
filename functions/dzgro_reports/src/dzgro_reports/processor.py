from bson import ObjectId
from db.collections.dzgro_reports import DzgroReportHelper
from db.collections.queue_messages import QueueMessagesHelper
from models.collections.dzgro_reports import DzgroReportType
from models.collections.queue_messages import DzgroReportQueueMessage
from dzgrosecrets import SecretManager
from dzgro_reports.pipelines import InventoryPlanning, OutOfStock, PaymentReconciliation
from fed_db import FedDbClient
from db import DbClient
from models.enums import CollateTypeTag
manager = SecretManager()
URI = manager.MONGO_DB_FED_CONNECT_URI

class DzgroReportProcessor:
    client: DbClient
    dzgroReportHelper: DzgroReportHelper
    queueMessagesHelper: QueueMessagesHelper
    fed: FedDbClient
    secrets: SecretManager

    def __init__(self, messageid: str, message: DzgroReportQueueMessage) -> None:
        self.messageid = messageid
        self.message = message
        self.secrets = SecretManager()
        self.client = DbClient(self.secrets.MONGO_DB_CONNECT_URI)
        self.dzgroReportHelper = self.client.dzgro_reports(self.message.uid, self.message.marketplace)
        self.queueMessagesHelper = self.client.sqs_messages()

    def __getattr__(self, item):
        return None

    def getFedDbClient(self):
        if self.fed: return self.fed
        self.fed = FedDbClient(self.secrets.MONGO_DB_FED_CONNECT_URI)
        return self.fed
    
    async def setMessageAsProcessing(self):
        updated, id = await self.queueMessagesHelper.setMessageAsProcessing(self.messageid)
        return updated==0
    
    async def setError(self, error: str):
        await self.queueMessagesHelper.setMessageAsFailed(self.messageid, error)
        await self.dzgroReportHelper.addError(self.message.index, error)

    async def processReport(self):
        try:
            
            if await self.setMessageAsProcessing():
                report = await self.dzgroReportHelper.getReport(self.message.index)
            if report.messageid==self.messageid:
                if report.reporttype==DzgroReportType.PAYMENT_RECON: 
                    orders = self.client.orders(self.message.uid, self.message.marketplace)
                    pipeline = PaymentReconciliation.pipeline(orders.db.pp, self.message.index)
                    await orders.db.aggregate(pipeline)
                elif report.reporttype==DzgroReportType.INVENTORY_PLANNING: 
                    _queries = self.client.queries(self.message.uid, self.message.marketplace)
                    queries = await _queries.getQueries()
                    query = next((q for q in queries if q.tag==CollateTypeTag.DAYS_30), None)
                    if query:
                        query_results = self.client.query_results(self.message.uid, self.message.marketplace)
                        pipeline = InventoryPlanning.pipeline(query_results.db.pp, self.message.index, str(query.id))
                        await query_results.db.aggregate(pipeline)
                    else: await self.setError("No query found for Inventory Planning")
                elif report.reporttype==DzgroReportType.OUT_OF_STOCK: 
                    products = self.client.products(self.message.uid, self.message.marketplace)
                    pipeline = OutOfStock.pipeline(products.db.pp, self.message.index)
                    await products.db.aggregate(pipeline)
                pipeline = [{"$match": {"reportid": ObjectId(self.message.index)}}]
                filename = f'{self.message.uid}/{str(self.message.marketplace)}/{report.reporttype.name}/{self.message.index}/data'
                self.getFedDbClient().createReport(filename, pipeline)
        except Exception as e:
            await self.setError(e.args[0] if e.args else str(e))

