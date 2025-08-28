from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.models.enums import CollectionType
from dzgroshared.models.model import PyObjectId


class OutofStockReport:
    client: DzgroSharedClient
    reportId: PyObjectId

    def __init__(self, client: DzgroSharedClient, reportId: PyObjectId ) -> None:
        self.client = client
        self.reportId = reportId

    async def execute(self):
        pipeline = self.pipeline(self.client.db.products.db.pp)
        await self.client.db.products.db.aggregate(pipeline)

    def pipeline(self, pp: PipelineProcessor):
        matchStage = pp.matchMarketplace({"childskus": {"$exists": False}, "quantity": {"$eq": 0}})
        project = pp.project(["sku","asin","quantity"],["_id"])
        setReportId = pp.set({'reportid': self.reportId})
        merge = pp.merge(CollectionType.DZGRO_REPORT_DATA)
        pipeline = [matchStage, project,setReportId,merge]
        return pipeline

