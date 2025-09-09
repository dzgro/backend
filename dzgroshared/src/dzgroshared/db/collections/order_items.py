from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class OrderItemsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ORDER_ITEMS), marketplace=client.marketplaceId)

    async def deleteOrderItems(self, orderIds: list[str]):
        if len(orderIds) > 0:
            await self.db.deleteMany({"order": {"$in": orderIds}})

