from dzgroshared.db.model import PeriodDataRequest
from dzgroshared.db.performance_periods.model import PerformancePeriodList
from dzgroshared.db.enums import CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class PerformancePeriodHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PERFORMANCE_PERIODS), marketplace=client.marketplaceId)

    async def buildQueriesAndResults(self):
        from .pipelines import CreateQueries, BuildResults
        await self.client.db.marketplaces.db.aggregate(CreateQueries.pipeline(self.client.marketplaceId))
        await self.client.db.performance_period_results.db.deleteMany({})
        pipeline = BuildResults.pipeline(self.client.marketplaceId)
        await self.db.aggregate(pipeline)

    async def getDashboardPerformanceResults(self, req: PeriodDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_comparison_pipeline(req)
        data = await self.db.aggregate(pipeline)
        return {"data": data}
    
    async def getPerformanceTableLite(self, body: PeriodDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_comparison_table_lite(body)
        data = await self.db.aggregate(pipeline)
        return data[0]

    async def getPerformancePeriods(self) -> PerformancePeriodList:
        data = await self.db.find({}, projectionExc=["marketplace", "createdat"])
        return PerformancePeriodList.model_validate({"data": data})
    
    
    
