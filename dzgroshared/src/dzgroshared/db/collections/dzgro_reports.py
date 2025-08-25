from bson import ObjectId
from dzgroshared.functions.DzgroReportsS3Trigger.models import S3TriggerDetails, S3TriggerObject, S3TriggerType
from dzgroshared.models.collections.dzgro_reports import ListDzgroReportsRequest, CreateDzgroReportRequest, DzgroReport
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.collections.queue_messages import DzgroReportQueueMessage
from dzgroshared.models.enums import ENVIRONMENT, CollectionType, QueueName, S3Bucket
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.sqs import SQSEvent, SendMessageRequest


class DzgroReportHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.client = client
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.DZGRO_REPORTS), uid, marketplace)

    def getReportTypes(self):
        from dzgroshared.models.collections import dzgro_reports
        return dzgro_reports.reportTypes

    async def createReport(self, request: CreateDzgroReportRequest):
        item = request.model_dump(exclude_none=True)
        item.update({"requested": self.db.date()})
        item = self.db.addUidMarketplaceToDict(item)
        id = await self.db.insertOne(item)
        reportId = str(id)
        message = DzgroReportQueueMessage(uid=self.uid, marketplace=self.marketplace, index=reportId, reporttype=request.reporttype)
        req = SendMessageRequest(QueueUrl=QueueName.DZGRO_REPORTS)
        res = await self.client.sqs.sendMessage(req, message)
        await self.addMessageId(reportId,res.message_id)
        if self.client.env==ENVIRONMENT.LOCAL:
            message = await self.client.db.sqs_messages.getMessage(res.message_id)
            sqsEvent = self.client.sqs.getSQSEventByMessage(res, message)
            from dzgroshared.functions.DzgroReports.handler import DzgroReportProcessor
            await DzgroReportProcessor(self.client).execute(sqsEvent)
            data = {"eventName": "ObjectCreated:Put", "s3": {"bucket": {"name": self.client.storage.getBucketName(bucket=S3Bucket.DZGRO_REPORTS), "arn": ""}, "object": {"key": f"{self.uid}/{self.client.marketplace}/{request.reporttype}/{reportId}/{request.reporttype}.parquet", "size": 0}}}
            from dzgroshared.functions.DzgroReportsS3Trigger.handler import DzgroReportS3TriggerProcessor
            await DzgroReportS3TriggerProcessor(self.client).execute(self.client.storage.getS3TriggerObject(data))
        return await self.getReport(reportId)

    def listReports(self, body: ListDzgroReportsRequest):
        matchDict = {"reporttype": body.reporttype} if body.reporttype else {}
        matchStage = self.db.pp.matchMarketplace(matchDict)
        skip = self.db.pp.skip(body.paginator.skip)
        limit = self.db.pp.limit(body.paginator.limit)
        pipeline = [matchStage, skip, limit]
        return self.db.aggregate(pipeline)
    
    async def getReport(self, reportid: str|ObjectId):
        return DzgroReport(**await self.db.findOne({'_id': self.db.convertToObjectId(reportid)}))

    async def addurl(self, reportid: str|ObjectId, url: str):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'url': url, "completed": self.db.date()})

    async def addCount(self, reportid: str|ObjectId, count: int):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'count': count})

    async def addError(self, reportid: str|ObjectId, error: str):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'error': error, "completed": self.db.date()})

    async def addMessageId(self, reportid: str|ObjectId, messageId: str):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'messageid': messageId})

    async def deleteReport(self, reportid: str|ObjectId):
        await self.db.deleteOne({'_id': self.db.convertToObjectId(reportid)})




        