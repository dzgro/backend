from bson import ObjectId
from dzgroshared.models.enums import CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class HealthHelper:
    db:DbManager
    uid: str
    marketplace: ObjectId

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.db = DbManager(client.db.database.get_collection(CollectionType.HEALTH.value), uid=self.uid)
        self.marketplace = marketplace

    async def getHealth(self):
        data = await self.db.findOne({"_id": self.marketplace}, projectionInc=["health"])
        return data['health']
    
    