from bson import ObjectId
from dzgroshared.models.collections.analytics import MarketplaceHealthResponse
from dzgroshared.db.marketplaces.model import MarketplaceCache
from dzgroshared.db.enums import CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.model import PyObjectId

class HealthHelper:
    client: DzgroSharedClient
    db:DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.HEALTH.value))

    async def getHealth(self):
        data = await self.db.findOne({"_id": self.client.marketplaceId}, projectionInc=["health"], projectionExc=["_id"])
        return MarketplaceHealthResponse.model_validate(data)
    
    