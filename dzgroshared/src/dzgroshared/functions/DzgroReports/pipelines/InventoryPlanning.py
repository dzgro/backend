from dzgroshared.models.enums import CollectionType
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.collections.pipelines.query_results import InventoryGroups

def pipeline(pp: PipelineProcessor, reportId: str, queryid: str):
    pipeline = InventoryGroups.execute(pp, queryid)
    pipeline.append(pp.project([],['uid','marketplace',"_id"]))
    pipeline.append(pp.set({'reportid': reportId}))
    pipeline.append(pp.merge(CollectionType.DZGRO_REPORT_DATA))
    return pipeline

