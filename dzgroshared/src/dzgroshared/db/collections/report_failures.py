from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.report_failures import DailyReportFailure
from dzgroshared.models.sqs import BatchMessageRequest
from pydantic import BaseModel
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType, SQSMessageStatus
from dzgroshared.models.collections.queue_messages import MODEL_REGISTRY

class DailyReportFailuresHelper:
    dbManager: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.dbManager = DbManager(client.db.database.get_collection(CollectionType.REPORT_FAILURES.value))

    async def addBatch(self, entries: list[dict]):
        return await self.dbManager.insertMany(entries)
