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
    from models.enums import AmazonDailyReportAggregationStep, SQSMessageStatus
    from bson import ObjectId
    import json
    from sqs import SqsHelper
    from dzgrosecrets import SecretManager
    from db import DbClient
    from sqs.model import QueueUrl, SQSEvent, SQSRecord, SendMessageRequest
    from models.model import MockLambdaContext
    from datetime import datetime
    marketplaceId = ObjectId("6895638c452dc4315750e826")
    uid= "41e34d1a-6031-70d2-9ff3-d1a704240921"
    
    messageId:str|None = "a63b618d-477b-4727-b62c-ed642ba3df4e"

    URI = SecretManager().MONGO_DB_CONNECT_URI
    dbClient = DbClient(URI)
    if not messageId:
        await dbClient.amazon_daily_reports(uid, marketplaceId).childDB.deleteMany({})
        await dbClient.amazon_daily_reports(uid, marketplaceId).groupDB.deleteMany({})
        await dbClient.sqs_messages().dbManager.deleteMany({})
        # await dbClient.settlements(uid, marketplaceId).db.deleteMany({})
        message = AmazonParentReportQueueMessage(
            marketplace =marketplaceId,
            uid =uid,
            step = AmazonDailyReportAggregationStep.CREATE_REPORTS,
        )
        messageId = (await SqsHelper(URI).mockMessage(SendMessageRequest(QueueUrl=QueueUrl.AMAZON_REPORTS, DelaySeconds=0), message)).message_id
    else:
        _message = await dbClient.sqs_messages().getMessage(messageId, SQSMessageStatus.PENDING)
        message = AmazonParentReportQueueMessage.model_validate(_message.model_dump())
    record = SQSRecord(
        messageId = messageId,
        receiptHandle ="",
        body = message.model_dump_json(),
        eventSource ="",
        eventSourceARN ="",
        awsRegion ="",
    )
    while record is not None:
        print(f'----------------{json.loads(record.body)['step']}----------------')
        context = MockLambdaContext(startTime=int(datetime.now().timestamp()*1000))
        res = await execute(SQSEvent(Records = [record]), context)
        if not res: record = None
        else: 
            message, messageId = res
            record.messageId = messageId
            record.body = message.model_dump_json()
        await asyncio.sleep(10)

asyncio.run(test())