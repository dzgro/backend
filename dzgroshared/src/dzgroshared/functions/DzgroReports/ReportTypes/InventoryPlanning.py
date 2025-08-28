from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.enums import CollateTypeTag, CollectionType
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.collections.pipelines.query_results import InventoryGroups
from dzgroshared.models.model import PyObjectId

class InventoryPlannerReport:
    client: DzgroSharedClient
    reportId: PyObjectId

    def __init__(self, client: DzgroSharedClient, reportId: PyObjectId ) -> None:
        self.client = client
        self.reportId = reportId

    async def execute(self):
        queries = await self.client.db.queries.getQueries()
        query = next((q for q in queries if q.tag==CollateTypeTag.DAYS_30), None)
        if query:
            pipeline = self.pipeline(self.client.db.query_results.db.pp, query.id)
            print(pipeline)
            await self.client.db.query_results.db.aggregate(pipeline)
        else: raise ValueError("No Sales Data for last 30 days")

    def pipeline(self, pp: PipelineProcessor, queryid: PyObjectId):
        pipeline = InventoryGroups.execute(pp, queryid)
        pipeline.append(pp.project([],['uid','marketplace',"_id"]))
        pipeline.append(pp.set({'reportid': self.reportId}))
        pipeline.append(pp.merge(CollectionType.DZGRO_REPORT_DATA))
        return pipeline

