from bson import ObjectId
from dzgroshared.db.dzgro_reports.model import CreateDzgroReportRequest, DzgroReport
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.queue_messages.model import DzgroReportQM
from dzgroshared.db.enums import ENVIRONMENT, CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.model import Paginator, Sort
from dzgroshared.sqs.model import QueueName, SQSEvent, SendMessageRequest
from dzgroshared.storage.model import S3Bucket


class DzgroReportHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.DZGRO_REPORTS),  marketplace=client.marketplaceId)


    async def createReport(self, request: CreateDzgroReportRequest):
        try:
            id = await self.db.insertOne(request.model_dump(exclude_none=True))
            reportId = str(id)
            message = DzgroReportQM(uid=self.client.uid, marketplace=self.client.marketplaceId, index=reportId, reporttype=request.reporttype)
            req = SendMessageRequest(Queue=QueueName.DZGRO_REPORTS, DelaySeconds=30)
            message_id = await self.client.sqs.sendMessage(req, message)
            await self.addMessageId(reportId,message_id)
            if self.client.env in ENVIRONMENT.LOCAL:
                message = await self.client.db.sqs_messages.getMessage(message_id)
                sqsEvent = self.client.sqs.getSQSEventByMessage(message_id, message)
                from dzgroshared.functions.DzgroReports.handler import DzgroReportProcessor
                await DzgroReportProcessor(self.client).execute(sqsEvent)
            return await self.getReport(reportId)
        except Exception as e:
            if not message_id: await self.client.db.dzgro_reports.deleteReport(reportId)
            else: await self.client.db.dzgro_reports.addError(reportId, str(e))
            raise e

    async def listReports(self, paginator: Paginator):
        reports = await self.db.find({}, skip=paginator.skip, limit=paginator.limit, sort=Sort(field='_id', order=-1))
        count = await self.db.count({})
        return { "reports": reports, "count": count }

    async def countReports(self):
        return await self.db.count({})

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




        