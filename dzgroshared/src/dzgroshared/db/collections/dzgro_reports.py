from bson import ObjectId
from dzgroshared.models.collections.dzgro_reports import CreateDzgroReportRequest, DzgroReport
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.collections.queue_messages import DzgroReportQueueMessage
from dzgroshared.models.enums import ENVIRONMENT, CollectionType, QueueName, S3Bucket
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import Paginator, Sort
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


    async def createReport(self, request: CreateDzgroReportRequest):
        try:
            id = await self.db.insertOne(request.model_dump(exclude_none=True), withUidMarketplace=True)
            reportId = str(id)
            print(reportId)
            message = DzgroReportQueueMessage(uid=self.uid, marketplace=self.marketplace, index=reportId, reporttype=request.reporttype)
            req = SendMessageRequest(Queue=QueueName.DZGRO_REPORTS, DelaySeconds=30)
            res = await self.client.sqs.sendMessage(req, message)
            await self.addMessageId(reportId,res.message_id)
            if self.client.env in ENVIRONMENT.LOCAL:
                message = await self.client.db.sqs_messages.getMessage(res.message_id)
                sqsEvent = self.client.sqs.getSQSEventByMessage(res, message)
                from dzgroshared.functions.DzgroReports.handler import DzgroReportProcessor
                await DzgroReportProcessor(self.client).execute(sqsEvent)
            return await self.getReport(reportId)
        except Exception as e:
            if not res.message_id: await self.client.db.dzgro_reports.deleteReport(reportId)
            else: await self.client.db.dzgro_reports.addError(reportId, str(e))
            raise e

    async def listReports(self, paginator: Paginator):
        return await self.db.find({}, skip=paginator.skip, limit=paginator.limit, sort=Sort(field='_id', order=-1))
        
    async def getReport(self, reportid: str|ObjectId):
        return DzgroReport(**await self.db.findOne({'_id': self.db.convertToObjectId(reportid)}))
    
    async def getDownloadUrl(self, reportid: str|ObjectId):
        report = await self.getReport(reportid)
        if report.error: raise ValueError("Report could not be generated")
        if not report.key: raise ValueError("Report not yet generated")
        return self.client.storage.create_signed_url_by_path(report.key, S3Bucket.DZGRO_REPORTS, 30)

    async def addKey(self, reportid: str|ObjectId, key: str):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'key': key}, markCompletion=True)

    async def addCount(self, reportid: str|ObjectId, count: int):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'count': count})

    async def addError(self, reportid: str|ObjectId, error: str):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'error': error}, markCompletion=True)

    async def addMessageId(self, reportid: str|ObjectId, messageId: str):
        await self.db.updateOne({'_id': self.db.convertToObjectId(reportid)}, {'messageid': messageId})

    async def deleteReport(self, reportid: str|ObjectId):
        await self.db.deleteOne({'_id': self.db.convertToObjectId(reportid)})




        