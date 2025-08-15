from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class SettlementsHelper:
    db: DbManager

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.db = DbManager(client.db.database.get_collection(CollectionType.SETTLEMENTS), uid, marketplace)

    async def getSettlementIds(self)->list[str]:
        return await self.db.distinct('settlementid')