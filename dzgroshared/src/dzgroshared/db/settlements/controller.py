from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class SettlementsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.SETTLEMENTS), marketplace=client.marketplaceId)

    async def getSettlementIds(self)->list[str]:
        return await self.db.distinct('settlementid')