from dzgroshared.db.performance_periods.model import PerformancePeriodList
from dzgroshared.db.performance_periods.pipelines import GetPerformancePeriods
from dzgroshared.db.enums import CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class PerformancePeriodHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PERFORMANCE_PERIODS))

    
    
    async def getPerformancePeriods(self) -> PerformancePeriodList:
        pipeline = GetPerformancePeriods.pipeline(self.client.marketplaceId)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        return PerformancePeriodList.model_validate({"data": data})
    
    
    
