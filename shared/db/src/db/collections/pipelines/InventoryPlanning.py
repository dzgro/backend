from db.pipelines.CreateInventoryLevels import InventoryProcessor
from db.PipelineProcessor import PipelineProcessor
from models.enums import CollectionType

async def execute(pp: PipelineProcessor, reportId: str):
    pipeline = InventoryProcessor(pp).execute()
    pipeline.append(pp.project([],['uid','marketplace',"_id"]))
    pipeline.append(pp.set({'reportid': reportId}))
    pipeline.append(pp.merge(CollectionType.DZGRO_REPORT_DATA))
    await pp.execute(CollectionType.QUERY_RESULTS, pipeline)

