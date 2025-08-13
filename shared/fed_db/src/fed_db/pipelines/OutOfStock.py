from app.HelperModules.Pipelines.Marketplace.PipelineProcessor import LookUpPipelineMatchExpression, PipelineProcessor, LookUpLetExpression
from app.HelperModules.Db.models import CollectionType

def execute(pp: PipelineProcessor, reportId: str):
    matchStage = pp.matchMarketplace({"childskus": {"$exists": False}, "quantity": {"$eq": 0}})
    project = pp.project(["sku","asin","quantity"],["_id"])
    setReportId = pp.set({'reportid': reportId})
    merge = pp.merge(CollectionType.DZGRO_REPORT_DATA)
    pipeline = [matchStage, project,setReportId,merge]
    pp.execute(CollectionType.PRODUCTS, pipeline)

