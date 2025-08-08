from bson import ObjectId
from db.DbUtils import DbManager
from models.enums import CollectionType
from motor.motor_asyncio import AsyncIOMotorDatabase

class SettlementsHelper:
    db: DbManager
    
    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.db = DbManager(db.get_collection(CollectionType.SETTLEMENTS), uid, marketplace)

    async def getSettlementIds(self)->list[str]:
        return await self.db.distinct('settlementid')