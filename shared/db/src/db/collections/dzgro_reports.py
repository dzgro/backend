from bson import ObjectId
from db.collections.queue_messages import QueueMessagesHelper
from models.collections.dzgro_reports import ListDzgroReportsRequest, CreateDzgroReportRequest, DzgroReport
from db.DbUtils import DbManager
from models.enums import CollectionType
from motor.motor_asyncio import AsyncIOMotorDatabase


class DzgroReportHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId, sqsHelper: QueueMessagesHelper) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(db.get_collection(CollectionType.DZGRO_REPORTS), uid, marketplace)
        self.sqsHelper = sqsHelper

    def getReportTypes(self):
        from models.collections import dzgro_reports
        return dzgro_reports.reportTypes

    async def createReport(self, request: CreateDzgroReportRequest):
        item = request.model_dump(exclude_none=True)
        item.update({"requested": self.db.date()})
        item = self.db.addUidMarketplaceToDict(item)
        id = self.db.insertOne(item)
        from sqs import SqsHelper
        sqs = SqsHelper(self.sqsHelper)
        reportId = str(id)
        res = sqs.sendMessage({"uid": self.uid, "marketplace": str(self.marketplace), "reportid": reportId}, delay=2)
        await self.addMessageId(reportId,res.message_id)
        return await self.getReport(reportId)

    def listReports(self, body: ListDzgroReportsRequest):
        matchDict = {"reporttype": body.reporttype} if body.reporttype else {}
        matchStage = self.db.pp.matchMarketplace(matchDict)
        skip = self.db.pp.skip(body.paginator.skip)
        limit = self.db.pp.limit(body.paginator.limit)
        pipeline = [matchStage, skip, limit]
        return self.db.aggregate(pipeline)
    
    async def getReport(self, reportid: str):
        return DzgroReport(**await self.db.findOne({'_id': ObjectId(reportid)}))

    async def addurl(self, reportid: str, url: str):
        await self.db.updateOne({'_id': ObjectId(reportid)}, {'url': url, "completed": self.db.date()})

    async def addError(self, reportid: str, error: str):
        await self.db.updateOne({'_id': ObjectId(reportid)}, {'error': error, "completed": self.db.date()})

    async def addMessageId(self, reportid: str, messageId: str):
        await self.db.updateOne({'_id': ObjectId(reportid)}, {'messageid': messageId})

    async def deleteReport(self, reportid: str):
        await self.db.deleteOne({'_id': ObjectId(reportid)})

    



        