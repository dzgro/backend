from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from bson import ObjectId
from dzgroshared.models.collections.analytics import PeriodDataRequest
from dzgroshared.models.enums import ENVIRONMENT, CollateType, CountryCode, QueueName
from dzgroshared.models.model import AnalyticsPeriodData, DataCollections, MockLambdaContext, StartEndDate


client = DzgroSharedClient(ENVIRONMENT.LOCAL)
uid = "41e34d1a-6031-70d2-9ff3-d1a704240921"
marketplace = ObjectId("6895638c452dc4315750e826")
client.setUid(uid)
client.setMarketplace(marketplace)
context = MockLambdaContext()
enddate = datetime(2025, 8, 31)
startdate= datetime(2025, 7, 3)
date_range = StartEndDate(startdate=startdate, enddate=enddate)


async def buildStateDateAnalytics():
    from dzgroshared.functions.AmazonDailyReport.reports.pipelines.Analytics import AnalyticsProcessor
    processor = AnalyticsProcessor(client, date_range)
    await processor.execute()
    print("Done")

async def buildQueries():
    from dzgroshared.db.collections.queries import QueryHelper
    await QueryHelper(client, uid, marketplace).buildQueries(date_range)
    print("Done")

async def testapi():
    data = await client.db.analytics.getPeriodData(PeriodDataRequest(collatetype=CollateType.MARKETPLACE, countrycode=CountryCode.INDIA))
    x = [AnalyticsPeriodData(**x) for x in data]
    print("Done")

async def deleteData():
    for collection in DataCollections:
        await client.db.database.get_collection(collection.value).delete_many({})

async def buildReports():
    # await deleteData()
    event = {"country": CountryCode.INDIA.value, "queue": QueueName.DAILY_REPORT_REFRESH_BY_COUNTRY_CODE.value}
    
    await client.functions(event, context).send_daily_report_refresh_message_to_queue

async def runReport():
    messageId = "4caf10ff-cd26-4fc5-920c-33ac80ad6915"

    event = client.sqs.mockSQSEvent(messageId, '')
    await client.functions(event, context).amazon_daily_report


def dates():
    from dzgroshared.utils import date_util
    dates = date_util.getEconomicsKioskReportDates('Asia/Kolkata', True)
    print(dates)
    dates = date_util.getAdReportDates('Asia/Kolkata',31, True)
    print(dates)
    dates = date_util.getSPAPIReportDates('Asia/Kolkata',31, True)
    print(dates)


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
    asyncio.run(buildStateDateAnalytics())
except Exception as e:
    print(f"Error occurred: {e}")