
import asyncio
from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.queue_messages import AmazonParentReportQueueMessage, DailyReportMessage
from dzgroshared.models.collections.report_failures import DailyReportFailure
from dzgroshared.models.enums import ENVIRONMENT, AmazonDailyReportAggregationStep, CollectionType, CountryCode, MarketplaceStatus, QueueName
from dzgroshared.models.model import LambdaContext, MockLambdaContext
from dzgroshared.models.sqs import BatchMessageRequest, SQSEvent, SQSRecord, SendMessageRequest
from dzgroshared.utils import date_util


class DailyReportRefreshByCountryCodeProcessor:
    client: DzgroSharedClient
    context: LambdaContext
    messageid: str

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event: dict, context: LambdaContext):
        self.context = context
        try:
            parsed = SQSEvent.model_validate(event)
            for record in parsed.Records:
                try:
                    self.messageid = record.messageId
                    message = DailyReportMessage.model_validate(record.dictBody)
                    return await self.buildMessages(message.index)
                except Exception as e:
                    await self.client.db.sqs_messages.setMessageAsFailed(self.messageid, str(e))
        except Exception as e:
            print(f"Error occurred: {e}")
            pass
        

    async def buildMessages(self, countryCode: CountryCode):
        marketplaces = self.client.db.database.get_collection(CollectionType.MARKETPLACES)
        pipeline = [{"$match": {"countrycode": countryCode.value, "status": MarketplaceStatus.ACTIVE.value}}]
        data = await marketplaces.aggregate(pipeline).to_list(length=None)
        batchRequests: list[BatchMessageRequest] = []
        for item in data:
            uid=item.get("uid")
            marketplace=item.get("_id")
            message = AmazonParentReportQueueMessage(
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
                    