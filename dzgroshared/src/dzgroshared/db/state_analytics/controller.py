from bson import ObjectId
from dzgroshared.analytics import controller
from dzgroshared.db.state_analytics.model import StateRequest
from dzgroshared.db.model import Month, MonthDataRequest
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager

class StateAnalyticsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.STATE_ANALYTICS.value), marketplace=client.marketplaceId)
    
    async def getStateDataDetailedForMonth(self, req: MonthDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_state_all_pipeline(req)
        rows = await self.client.db.marketplaces.db.aggregate(pipeline)
        columns = controller.convertSchematoMultiLevelColumns('State All')
        return {"columns": columns, "rows": rows, **req.model_dump(exclude_none=True)}

    async def getStateDataLiteByMonth(self, req: MonthDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_state_lite_pipeline(req)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        return {"data": data}
    
    async def getStateDataDetailed(self, req: StateRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_state_detail_pipeline(req)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        if not data: raise ValueError("No data found for the given request")
        return data[0]
