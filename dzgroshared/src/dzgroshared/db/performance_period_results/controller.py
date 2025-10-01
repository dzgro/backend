from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.performance_period_results.model import ComparisonTableRequest, PerformanceDashboardResponse, PerformanceTableResponse
from dzgroshared.db.enums import CollectionType, CollateType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.analytics import controller
from dzgroshared.db.model import PeriodDataRequest


class PerformancePeriodResultsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PERFORMANCE_PERIOD_RESULTS), marketplace=client.marketplaceId)


    async def deletePerformanceResults(self, queryid: ObjectId|None=None):
        filterDict = {"queryid": queryid} if queryid else {}
        await self.db.deleteMany(filterDict)
    
    async def getCount(self, body: ComparisonTableRequest):
        matchDict = {"queryid": body.queryId, "collatetype": body.collatetype.value}
        if body.parent: matchDict.update({"parent": body.parent})
        return {"count": await self.db.count(matchDict)}
    
    async def getPerformanceTable(self, body: ComparisonTableRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_comparison_table_pipeline(body)
        data = await self.db.aggregate(pipeline)
        columns = ["Skus" if body.collatetype==CollateType.SKU else "Asins" if body.collatetype==CollateType.ASIN else "Parent Skus" if body.collatetype==CollateType.PARENT else "Category"]
        columns.extend([item.metric.value for item in controller.getMetricGroupsBySchemaType('Comparison', body.collatetype)])
        return {"rows": data, "columns": columns}
    
    async def getPerformanceTableLite(self, body: PeriodDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_comparison_table_lite(body)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        return data[0]

    async def getDashboardPerformanceResults(self, req: PeriodDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_comparison_pipeline(req)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        return {"data": data}
        return PerformanceDashboardResponse.model_validate({"data": data})
    
    


        
      
    

        

