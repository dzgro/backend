
import asyncio
from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.queue_messages.model import AmazoMarketplaceDailyReportQM, DailyReportByCountryQM
from dzgroshared.db.enums import ENVIRONMENT, AmazonDailyReportAggregationStep, CollectionType, CountryCode, MarketplaceStatus
from dzgroshared.db.model import LambdaContext
from dzgroshared.sqs.model import BatchMessageRequest, QueueName, SQSEvent, SQSRecord


class DailyReportRefreshByCountryCodeProcessor:
    client: DzgroSharedClient
    context: LambdaContext
    messageid: str

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, context,  record: SQSRecord):
        self.context = context
        self.messageid = record.messageId
        message = DailyReportByCountryQM.model_validate(record.dictBody)
        return await self.buildMessages(message.index)
            
        

    async def buildMessages(self, countryCode: CountryCode):
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
        await self.client.db.sqs_messages.setMessageAsCompleted(self.messageid, extras)
        if(self.client.env==ENVIRONMENT.LOCAL):
            for success in res.Success:
                body = next((doc.Body for doc in batchRequests if doc.Id == success.Id), None)
                if body:
                    sqsEvent = self.client.sqs.mockSQSEvent(success.MessageID, body.model_dump_json(exclude_none=True))
                    await self.client.functions(sqsEvent, self.context).amazon_daily_report
                    