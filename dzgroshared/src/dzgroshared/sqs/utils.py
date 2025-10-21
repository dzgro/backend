from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import ENVIRONMENT, AmazonDailyReportAggregationStep, CollectionType, CountryCode, MarketplaceStatus
from dzgroshared.db.model import LambdaContext, MockLambdaContext, PyObjectId
from dzgroshared.db.queue_messages.model import AmazoMarketplaceDailyReportQM
from dzgroshared.sqs.model import BatchMessageRequest, QueueName, ReceiveMessageRequest, SQSEvent, SQSRecord

class SQSUtils:
    client: DzgroSharedClient
    record: SQSRecord
    context: LambdaContext
    
    def __init__(self, client: DzgroSharedClient, record: SQSRecord, context: LambdaContext = MockLambdaContext()) -> None:
        self.client = client
        self.record = record
        self.context = context
        
    async def getMessageFromDevQueue(self, queueName: QueueName, messageId: str):
        req = ReceiveMessageRequest(QueueUrl=queueName)
        messages: SQSEvent
        hasMore = True
        while hasMore:
            messages = await self.client.sqs.getMessages(req)
            messageReceived = next((x for x in messages.Records if x.messageId==messageId), None)
            if messageReceived:
                await self.client.sqs.deleteMessage(queueName, messageReceived.receiptHandle)
            hasMore = len(messages.Records)==0 and messageReceived is None
        if not hasMore: raise ValueError(f"Message not found in Queue {queueName.value}")
        return messages.model_dump(mode="json", exclude_none=True)
        
        
    async def executeAmazonReportsByCountryCode(self, countryCode: CountryCode):
        res, batchRequests = await self._startAmazonReports(countryCode)
        if(self.client.env==ENVIRONMENT.DEV):
            for success in res.Success:
                body = next((doc.Body for doc in batchRequests if doc.Id == success.Id), None)
                if body:
                    sqsEvent = await self.getMessageFromDevQueue(QueueName.DAILY_REPORT_REFRESH_BY_COUNTRY_CODE, success.MessageID)
                    await self.client.functions(sqsEvent, self.context).amazon_daily_report
                    
    async def executeInvoiceGenerator(self, orderid: str, paymentid: str):
        from dzgroshared.sqs.model import SendMessageRequest, QueueName
        from dzgroshared.db.queue_messages.model import GenerateInvoiceQM
        messageRequest = SendMessageRequest(Queue=QueueName.INVOICE_GENERATOR)
        body = GenerateInvoiceQM(orderid=orderid, paymentid=paymentid, uid=self.client.uid)
        messageId =  await self.client.sqs.sendMessage(messageRequest, body)
        if(self.client.env==ENVIRONMENT.DEV):
            sqsEvent = await self.getMessageFromDevQueue(QueueName.INVOICE_GENERATOR, messageId)
            await self.client.functions(sqsEvent, self.context).invoice_generator
        
    async def sendCreateReportsMessage(self, marketplace: PyObjectId):
        from dzgroshared.sqs.model import SendMessageRequest, QueueName
        from dzgroshared.db.queue_messages.model import AmazoMarketplaceDailyReportQM, AmazonDailyReportAggregationStep
        req = SendMessageRequest(Queue=QueueName.AMAZON_REPORTS)
        body = AmazoMarketplaceDailyReportQM(marketplace=marketplace, step=AmazonDailyReportAggregationStep.CREATE_REPORTS, uid=self.client.uid)
        messageId = await self.client.sqs.sendMessage(req, body)
        if(self.client.env==ENVIRONMENT.DEV):
            sqsEvent = await self.getMessageFromDevQueue(QueueName.AMAZON_REPORTS, messageId)
            await self.client.functions(sqsEvent, self.context).amazon_daily_report
        
    async def _startAmazonReports(self, countryCode: CountryCode):
        marketplaces = self.client.db.database.get_collection(CollectionType.MARKETPLACES)
        pipeline = [{"$match": {"countrycode": countryCode.value, "status": MarketplaceStatus.ACTIVE.value}}]
        data = await marketplaces.aggregate(pipeline).to_list(length=None)
        batchRequests: list[BatchMessageRequest] = []
        for item in data:
            uid=item.get("uid")
            marketplace=item.get("_id")
            message = AmazoMarketplaceDailyReportQM(
                uid=uid,
                marketplace=marketplace,
                step=AmazonDailyReportAggregationStep.CREATE_REPORTS,
            )
            req = BatchMessageRequest(
                Body=message,
                Id=f'{uid}-{str(marketplace)}',
            )
            batchRequests.append(req)
        res = await self.client.sqs.sendBatchMessage(QueueName.AMAZON_REPORTS, batchRequests)
        batch: list[dict] = []
        now = datetime.now()
        for failure in res.Failed:
            batch.append({
                'message': failure.model_dump(),
                'marketplace': failure.Id.split('-')[-1],
                'createdat': now
            })
        if batch: 
            await self.client.db.daily_report_failures.addBatch(batch)
        extras = {'success': len(res.Success), 'failed': len(res.Failed), 'total': len(batchRequests)}
        await self.client.db.sqs_messages.setMessageAsCompleted(self.record.messageId, extras)
        return res, batchRequests
    