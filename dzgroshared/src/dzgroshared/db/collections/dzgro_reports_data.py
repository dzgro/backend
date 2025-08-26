from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class DzgroReportDataHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.client = client
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.DZGRO_REPORT_DATA))

    async def count(self, reportid: str|ObjectId):
        return await self.db.count({'reportid': self.db.convertToObjectId(reportid)})

    



        