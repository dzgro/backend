from db.PipelineProcessor import PipelineProcessor
from models.enums import CollectionType

async def execute(pp: PipelineProcessor, reportId: str):
    matchStage = pp.matchMarketplace({"childskus": {"$exists": False}, "quantity": {"$eq": 0}})
    project = pp.project(["sku","asin","quantity"],["_id"])
    setReportId = pp.set({'reportid': reportId})
    merge = pp.merge(CollectionType.DZGRO_REPORT_DATA)
    pipeline = [matchStage, project,setReportId,merge]
    await pp.execute(CollectionType.PRODUCTS, pipeline)

