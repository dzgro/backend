from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class OrderItemsHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.ORDER_ITEMS), uid, marketplace)

    async def deleteOrderItems(self, orderIds: list[str]):
        if len(orderIds) > 0:
            await self.db.deleteMany({"order": {"$in": orderIds}})

