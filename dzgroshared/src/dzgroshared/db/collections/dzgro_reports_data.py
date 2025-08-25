from bson import ObjectId
from dzgroshared.functions.DzgroReportsS3Trigger.models import S3TriggerDetails, S3TriggerObject, S3TriggerType
from dzgroshared.models.collections.dzgro_reports import ListDzgroReportsRequest, CreateDzgroReportRequest, DzgroReport
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.collections.queue_messages import DzgroReportQueueMessage
from dzgroshared.models.enums import ENVIRONMENT, CollectionType, QueueName, S3Bucket
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.sqs import SQSEvent, SendMessageRequest


class DzgroReportDataHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.client = client
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.DZGRO_REPORT_DATA), uid, marketplace)

    async def count(self, reportid: str|ObjectId):
        return await self.db.count({'reportid': self.db.convertToObjectId(reportid)})

    



        