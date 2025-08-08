from amazon_daily_report.reports.ReportApp import AmazonReportManager
from sqs.model import SQSEvent
from models.collections.queue_messages import AmazonParentReportQueueMessage
import asyncio

async def handler(event: dict, context):
    return asyncio.run(execute(SQSEvent(**event), context))


async def execute(event: SQSEvent, context):
    try:
        parsed = SQSEvent.model_validate(event)
        for record in parsed.Records: 
            message = AmazonParentReportQueueMessage.model_validate(record.dictBody)
            return await AmazonReportManager(record.messageId, message, context).checkMessage()
    except Exception as e:
        print(f"[ERROR] Failed to process message {record.messageId}: {e}")
        raise


async def test():
    from models.enums import AmazonDailyReportAggregationStep
    from bson import ObjectId
    from sqs import SqsHelper
    from dzgrosecrets import SecretManager
    from sqs.model import QueueUrl, SQSEvent, SQSRecord, SendMessageRequest
    from models.model import MockLambdaContext
    from datetime import datetime
    marketplaceId = ObjectId("6895638c452dc4315750e826")
    uid= "41e34d1a-6031-70d2-9ff3-d1a704240921"
    message = AmazonParentReportQueueMessage(
                marketplace =marketplaceId,
                uid =uid,
                # index="6874e2fa6c990ccda53e9047",
                step = AmazonDailyReportAggregationStep.CREATE_REPORTS,
            )
    record = SQSRecord(
        messageId = "af9c4090-3f9d-4b95-89b0-c3b03b403522",
        receiptHandle ="",
        body = message.model_dump_json(),
        eventSource ="",
        eventSourceARN ="",
        awsRegion ="",
    )
    URI = SecretManager().MONGO_DB_CONNECT_URI
    if len(record.messageId)==0: record.messageId = (await SqsHelper(URI).mockMessage(SendMessageRequest(QueueUrl=QueueUrl.AMAZON_REPORTS, DelaySeconds=0), message)).message_id
    while message is not None:
        print(f'----------------{message.step.value}----------------')
        print(record.messageId)
        context = MockLambdaContext(startTime=int(datetime.now().timestamp()*1000))
        res = await execute(SQSEvent(Records = [record]), context)
        if not res: message = None
        else: 
            message, messageId = res
            record.messageId = messageId
            record.body = message.model_dump_json()

asyncio.run(test())