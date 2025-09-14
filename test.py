from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from bson import ObjectId
import inspect

from dzgroshared.db.marketplaces.model import MarketplaceCache
from dzgroshared.db.enums import ENVIRONMENT, CollateType, CountryCode, MarketplaceId, QueueName
from dzgroshared.db.model import DataCollections, MockLambdaContext, Paginator, PyObjectId, Sort, StartEndDate

env = ENVIRONMENT.LOCAL
# client = DzgroSharedClient(env)
uid = "41e34d1a-6031-70d2-9ff3-d1a704240921"
marketplaceId=  PyObjectId("6895638c452dc4315750e826")
marketplace = MarketplaceCache(_id=marketplaceId, uid=uid, countrycode=CountryCode.INDIA, marketplaceid=MarketplaceId.IN,profileid=476214271739435, sellerid="AUYWKTHB2JM7A") 
# DB_NAME = f'dzgro-{env.value.lower()}' if env != ENVIRONMENT.LOCAL else 'dzgro-dev'
# client.setUid(uid)
# client.setMarketplace(marketplace)
# context = MockLambdaContext()
# enddate = datetime(2025, 8, 31)
# startdate= datetime(2025, 7, 3)
# date_range = StartEndDate(startdate=startdate, enddate=enddate)
# queryId=PyObjectId("686750af5ec9b6bf57fe9060")


async def buildStateDateAnalyticsAndQueries():
    from dzgroshared.functions.AmazonDailyReport.reports.pipelines.Analytics import AnalyticsProcessor
    processor = AnalyticsProcessor(client, date_range)
    await processor.execute()
    from dzgroshared.analytics import controller
    pipeline = controller.getQueriesPipeline(client.marketplaceId, date_range)
    await client.db.query_results.deleteQueryResults()
    await client.db.marketplaces.db.aggregate(pipeline)
    print("Done")

async def testapi():
    from dzgroshared.models.collections.analytics import PeriodDataResponse, PeriodDataRequest, ComparisonPeriodDataRequest,PerformancePeriodDataResponse,MonthDataRequest, StateMonthDataResponse,StateDetailedDataByStateRequest, StateDetailedDataResponse, AllStateData,MonthTableResponse, MonthDataResponse,MonthDateTableResponse
    from dzgroshared.db.performance_period_results.model import PerformanceTableRequest, PerformanceTableResponse
    # periodreq = PeriodDataRequest(collatetype=CollateType.MARKETPLACE, value=None)
    # comparisonreq = ComparisonPeriodDataRequest(collatetype=CollateType.MARKETPLACE, value=None, queryId=queryId)
    # monthreq = MonthDataRequest(collatetype=CollateType.MARKETPLACE, value=None, month="Jul 2025")
    # stateDetailsReq = StateDetailedDataByStateRequest(collatetype=CollateType.MARKETPLACE, value=None, state="Karnataka")
    # paginator = Paginator(skip=0, limit=10)
    # sort = Sort(field="revenue", order=-1)
    # performanceRequest = PerformanceTableRequest(collatetype=CollateType.SKU, queryId=queryId, value="Mad PD PC S 122", paginator=paginator, sort=sort)

    def showStatus(frame, SUCCESS: bool=True):
        if not frame: raise ValueError("Frame is required")
        print(f"{'Success' if SUCCESS else 'Failed'}: {frame.f_code.co_name.replace('_'," ").title()}")

    async def dzgroshared()->DzgroSharedClient:
        from motor.motor_asyncio import AsyncIOMotorClient
        shared = DzgroSharedClient(env)
        shared.setMongoClient(AsyncIOMotorClient(shared.secrets.MONGO_DB_CONNECT_URI, appname="dzgro-api"))
        shared.setUid(uid)
        collection = shared.mongoClient[shared.DB_NAME]['marketplaces']
        m = await collection.find_one({"_id": ObjectId(marketplaceId), "uid": uid})
        marketplaceCache = MarketplaceCache.model_validate(m)
        shared.setMarketplace(marketplaceCache)
        return shared

    async def getMarketplaces():
        client = await dzgroshared()
        await client.db.marketplaces.getMarketplaces(paginator)
        showStatus( inspect.currentframe())

    async def get_performance_table():
        data = await client.db.query_results.getPerformanceListforPeriod(performanceRequest)
        PerformanceTableResponse.model_validate(data)
        

    async def get_period_data():
        data = await client.db.analytics.getPeriodData(periodreq)
        PeriodDataResponse.model_validate(data)
        showStatus( inspect.currentframe())

    async def get_health():
        await client.db.health.getHealth()
        showStatus( inspect.currentframe())

    async def get_period_data_comparison():
        data = await client.db.query_results.getPerformanceforPeriod(comparisonreq)
        PerformancePeriodDataResponse.model_validate(data)
        showStatus( inspect.currentframe())

    async def get_state_data_lite_by_month():
        data = await client.db.analytics.getStateDataLiteByMonth(monthreq)
        StateMonthDataResponse.model_validate(data)
        showStatus( inspect.currentframe())

    async def get_data_for_state():
        data = await client.db.analytics.getStateDataDetailed(stateDetailsReq)
        StateDetailedDataResponse.model_validate(data)
        showStatus( inspect.currentframe())

    async def get_state_data_for_month():
        data = await client.db.analytics.getStateDataDetailedForMonth(monthreq)
        AllStateData.model_validate(data)
        showStatus( inspect.currentframe())

    async def get_month_data():
        data = await client.db.analytics.getMonthlyDataTable(periodreq)
        MonthTableResponse.model_validate(data)
        showStatus( inspect.currentframe())

    async def get_month_dates_data():
        data = await client.db.analytics.getMonthDatesDataTable(monthreq)
        MonthDateTableResponse.model_validate(data)
        showStatus( inspect.currentframe())

    async def get_month_lite_data():
        data = await client.db.analytics.getMonthLiteData(monthreq)
        MonthDataResponse.model_validate(data)
        showStatus( inspect.currentframe())

    try:    
        # await get_health()
        # await get_state_data_lite_by_month()
        # await get_data_for_state()
        # await get_state_data_for_month()
        # await get_month_data()
        # await get_month_dates_data()
        # await get_month_lite_data()
        # await get_period_data()
        # await get_period_data_comparison()
        # await get_performance_table()
        await getMarketplaces()
        print("Done")
    except Exception as e:
        print(f"Error occurred: {e}")

async def deleteData():
    for collection in DataCollections:
        await client.db.database.get_collection(collection.value).delete_many({})

async def buildReports():
    # await deleteData()
    event = {"country": CountryCode.INDIA.value, "queue": QueueName.DAILY_REPORT_REFRESH_BY_COUNTRY_CODE.value}
    await client.functions(event, context).send_daily_report_refresh_message_to_queue

async def runReport():
    messageId = '8ce77c23-2958-41fd-8f9d-b32845a214ab'
    await  client.db.sqs_messages.setMessageAsPending(messageId)
    message = await client.db.sqs_messages.getAmazonParentReportQueueMessage(messageId)
    event = client.sqs.mockSQSEvent(messageId, message.model_dump_json(exclude_none=True))
    await client.functions(event, context).amazon_daily_report

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
    asyncio.run(testapi())
except Exception as e:
    print(f"Error occurred: {e}")