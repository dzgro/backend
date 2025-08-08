from bson import ObjectId
from db.DbUtils import DbManager
from models.enums import CollectionType
from motor.motor_asyncio import AsyncIOMotorDatabase

class OrderItemsHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    
    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(db.get_collection(CollectionType.ORDER_ITEMS), uid, marketplace)

    async def deleteOrderItems(self, orderIds: list[str]):
        if len(orderIds) > 0:
            await self.db.deleteMany({"order": {"$in": orderIds}})

