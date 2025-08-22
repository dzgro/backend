from datetime import datetime, timedelta
from dzgroshared.client import DzgroSharedClient
from bson import ObjectId
from dzgroshared.models.enums import ENVIRONMENT, CollectionType


client = DzgroSharedClient()
uid = "41e34d1a-6031-70d2-9ff3-d1a704240921"
marketplace = ObjectId("6895638c452dc4315750e826")
client.setUid(uid)
client.setMarketplace(marketplace)
enddate = datetime(2025, 8, 8)
startdate= datetime(2025, 6, 10)
dates = [startdate + timedelta(days=i) for i in range((enddate - startdate).days + 1)]

async def buildQueries():
    from dzgroshared.functions.AmazonDailyReport.reports.pipelines.ProductQueryBuilder import QueryBuilder
    builder = QueryBuilder(client.db, startdate, enddate)
    query = await builder.getNextQuery(None)
    while query is not None:
        query = await builder.execute(query)
    print("Done")

async def buildStateDateAnalytics():
    from dzgroshared.functions.AmazonDailyReport.reports.pipelines.StateAndDateAnalytics import AnalyticsProcessor
    processor = AnalyticsProcessor(client.db, dates)
    from dzgroshared.models.enums import CollateType
    collateTypes: list[CollateType] = [CollateType.SKU]
    date = await processor.executeDate(dates.pop(), collateTypes)
    while date:
        date = await processor.executeDate(dates.pop(), collateTypes)
    print("Done")

async def buildReports():
    from dzgroshared.models.collections.queue_messages import AmazonParentReportQueueMessage
    from dzgroshared.models.enums import AmazonDailyReportAggregationStep
    from dzgroshared.models.model import MockLambdaContext, DataCollections
    from dzgroshared.models.sqs import SendMessageRequest, QueueUrl, ReceiveMessageRequest, DeleteMessageBatchEntry, DeleteMessageBatchRequest
    QueueUrl = QueueUrl.AMAZON_REPORTS_TEST
    startfresh = False
    if startfresh:
        while startfresh:
            sqsevent = await client.sqs.getMessages(ReceiveMessageRequest(QueueUrl=QueueUrl, MaxNumberOfMessages=1))
            startfresh = sqsevent.has_messages
            for message in sqsevent.messages: await client.sqs.deleteMessage(queue=QueueUrl, receipt_handle=message.receiptHandle)
        message = AmazonParentReportQueueMessage(
            marketplace=client.marketplace,
            uid=client.uid,
            step=AmazonDailyReportAggregationStep.CREATE_REPORTS
        )
        index: ObjectId|None = None
        if message.step == AmazonDailyReportAggregationStep.CREATE_REPORTS:
            collections = DataCollections
            for collection in collections:
                if collection in [
                    CollectionType.ADV_ASSETS, 
                    CollectionType.QUEUE_MESSAGES,
                    CollectionType.AMAZON_CHILD_REPORT,
                    CollectionType.AMAZON_CHILD_REPORT_GROUP]:
                    await client.db.database.get_collection(collection.value).delete_many({})
        elif index is not None: message.index = index
        else: raise ValueError("Index is required for this step")
        await client.sqs.sendMessage(SendMessageRequest(QueueUrl=QueueUrl, DelaySeconds=0), message)
    from dzgroshared.functions.AmazonDailyReport.handler import AmazonReportManager
    manager = AmazonReportManager(client)
    shouldContinue = True
    while shouldContinue:
        sqsevent = await client.sqs.getMessages(ReceiveMessageRequest(QueueUrl=QueueUrl, MaxNumberOfMessages=1))
        shouldContinue = sqsevent.has_messages
        if shouldContinue:
            res = await manager.execute(sqsevent, MockLambdaContext())
            if client.env==ENVIRONMENT.DEV: 
                req = DeleteMessageBatchRequest(QueueUrl=QueueUrl, Entries=[
                    DeleteMessageBatchEntry(Id=record.messageId, ReceiptHandle=record.receiptHandle)
                    for record in sqsevent.Records
                ])
                await client.sqs.deleteMessageBatch(req)
            shouldContinue = res is not None
            if res and res>0: await asyncio.sleep(res+2)


async def estimate_db_reclaimable_space():
    stats = await client.db.database.command("dbStats", 1, scale=1)

    logical = stats.get("dataSize", 0)       # Total size of all documents
    storage = stats.get("storageSize", 0)    # Disk space allocated
    free = stats.get("freeStorageSize", storage - logical)  # MongoDB 6.0+ has this

    def to_mb(bytes_val):
        return round(bytes_val / (1024 * 1024), 2)

    print(f"Logical Size: {to_mb(logical)} MB")
    print(f"Storage Size: {to_mb(storage)} MB")
    print(f"Free/Fragmented Space: {to_mb(free)} MB")
    print(f"Potential Reclaim if Compact/Repair: {to_mb(free)} MB")


import asyncio
try:
    asyncio.run(estimate_db_reclaimable_space())
except Exception as e:
    print(f"Error occurred: {e}")