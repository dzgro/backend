from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollectionType

class DailyReportFailuresHelper:
    dbManager: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.dbManager = DbManager(client.db.database.get_collection(CollectionType.REPORT_FAILURES.value))

    async def addBatch(self, entries: list[dict]):
        return await self.dbManager.insertMany(entries)
