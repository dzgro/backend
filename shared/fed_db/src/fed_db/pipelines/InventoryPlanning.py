from app.HelperModules.Collections.dzgro.query_results.pipelines.CreateInventoryLevels import InventoryProcessor
from app.HelperModules.Pipelines.Marketplace.PipelineProcessor import LookUpPipelineMatchExpression, PipelineProcessor, LookUpLetExpression
from app.HelperModules.Db.models import CollectionType
def execute(pp: PipelineProcessor, reportId: str):
    pipeline = InventoryProcessor(pp).execute()
    pipeline.append(pp.project([],['uid','marketplace',"_id"]))
    pipeline.append(pp.set({'reportid': reportId}))
    pipeline.append(pp.merge(CollectionType.DZGRO_REPORT_DATA))
    pp.execute(CollectionType.QUERY_RESULTS, pipeline)

