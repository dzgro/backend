from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.model import PyObjectId


async def sendGenerateInvoiceMessage(client: DzgroSharedClient, orderid: str, paymentid: str):
    from dzgroshared.sqs.model import SendMessageRequest, QueueName
    from dzgroshared.db.queue_messages.model import GenerateInvoiceQM
    messageRequest = SendMessageRequest(Queue=QueueName.INVOICE_GENERATOR)
    body = GenerateInvoiceQM(orderid=orderid, paymentid=paymentid, uid=client.uid)
    await client.sqs.sendMessage(messageRequest, body)
    
async def sendCreateReportsMessage(client: DzgroSharedClient, marketplace: PyObjectId):
    from dzgroshared.sqs.model import SendMessageRequest, QueueName
    from dzgroshared.db.queue_messages.model import AmazoMarketplaceDailyReportQM, AmazonDailyReportAggregationStep
    req = SendMessageRequest(Queue=QueueName.AMAZON_REPORTS)
    body = AmazoMarketplaceDailyReportQM(marketplace=marketplace, step=AmazonDailyReportAggregationStep.CREATE_REPORTS, uid=client.uid)
    await client.sqs.sendMessage(req, body)