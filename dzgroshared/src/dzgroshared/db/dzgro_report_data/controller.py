from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class DzgroReportDataHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.DZGRO_REPORT_DATA))

    async def count(self, reportid: str|ObjectId):
        return await self.db.count({'reportid': self.db.convertToObjectId(reportid)})

    async def deleteReportData(self, reportid: str|ObjectId):
        return await self.db.deleteMany({'reportid': self.db.convertToObjectId(reportid)})  

        