from bson import ObjectId
from models.enums import CollectionType
from db.DbUtils import DbManager
from motor.motor_asyncio import AsyncIOMotorDatabase

class HealthHelper:
    db:AsyncIOMotorDatabase
    uid: str
    marketplace: ObjectId

    def __init__(self, db:AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.db = db
        self.marketplace = marketplace

    async def getHealth(self):
        db = DbManager(self.db.get_collection(CollectionType.HEALTH.value), uid=self.uid)
        data = await db.findOne({"_id": self.marketplace}, projectionInc=["health"])
        return data['health']
    
    