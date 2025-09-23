from bson import ObjectId
from dzgroshared.db.health.model import MarketplaceHealthResponse
from dzgroshared.db.enums import CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class HealthHelper:
    client: DzgroSharedClient
    db:DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.HEALTH.value))

    async def getHealth(self):
        data = await self.db.findOne({"_id": self.client.marketplaceId}, projectionInc=["health"], projectionExc=["_id"])
        return MarketplaceHealthResponse.model_validate(data)
    
    