from bson import ObjectId
from models.collections.dzgro_reports import ListDzgroReportsRequest, CreateDzgroReportRequest, DzgroReport, DzgroReportType
from db.collections.pipelines import PaymentReconciliation, InventoryPlanning, OutOfStock
from db.DbUtils import DbManager
from db.FedDbUtils import FedDbManager
from models.enums import CollectionType, FederationCollectionType

from motor.motor_asyncio import AsyncIOMotorDatabase


class DzgroReportHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    
    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(db.get_collection(CollectionType.DZGRO_REPORTS), uid, marketplace)

    def getReportTypes(self):
        from models.collections import dzgro_reports
        return dzgro_reports.reportTypes

    async def createReport(self, request: CreateDzgroReportRequest):
        item = request.model_dump(exclude_none=True)
        item.update({"requested": self.db.date()})
        item = self.db.addUidMarketplaceToDict(item)
        id = self.db.insertOne(item)
        from app.HelperModules.Helpers.SqsHelper.Sqs import SqsHelper, QueueUrl
        reportId = str(id)
        res = SqsHelper().sendMessage({"uid": self.uid, "marketplace": str(self.marketplace), "reportid": reportId}, delay=2)
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

    async def addMessageId(self, reportid: str, messageId: str):
        await self.db.updateOne({'_id': ObjectId(reportid)}, {'messageid': messageId})

    async def deleteReport(self, reportid: str):
        await self.db.deleteOne({'_id': ObjectId(reportid)})

    async def processReport(self, reportid: str, messageId: str):
        try:
            report = await self.getReport(reportid)
            if report.messageid==messageId:
                if report.reporttype==DzgroReportType.PAYMENT_RECON: await PaymentReconciliation.execute(self.db.pp, reportid)
                elif report.reporttype==DzgroReportType.INVENTORY_PLANNING: await InventoryPlanning.execute(self.db.pp, reportid)
                elif report.reporttype==DzgroReportType.OUT_OF_STOCK: await OutOfStock.execute(self.db.pp, reportid)
                pipeline = [{"$match": {"reportid": reportid}}]
                filename = f'{self.uid}/{str(self.marketplace)}/{report.reporttype.name}/{reportid}/data'
                fedDb = FedDbManager(FederationCollectionType.DZGRO_REPORT_DATA, self.marketplace, self.uid)
                fedDb.write(filename, pipeline)
                print("Done")
        except Exception as e:
            print(e)
            pass



        