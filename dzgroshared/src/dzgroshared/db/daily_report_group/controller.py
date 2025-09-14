from dzgroshared.db.model import StartEndDate
from dzgroshared.db.daily_report_group.model import AmazonParentReport
from pymongo.collection import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import AmazonParentReportTaskStatus, AmazonReportType, CollectionType
from dzgroshared.client import DzgroSharedClient

class DailyReportGroupHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.DAILY_REPORT_GROUP.value), marketplace=self.client.marketplaceId)

    async def insertParentReport(self, dates: StartEndDate):
        id = await self.db.insertOne({'status':AmazonParentReportTaskStatus.PROCESSING.value, 'dates': dates.model_dump()})
        return id

    async def updateParentReportStatus(self, id: ObjectId, status: AmazonParentReportTaskStatus):
        await self.db.updateOne({"_id": id}, setDict={'status': status.value})

    async def markReportsComplete(self, id: ObjectId):
        await self.db.updateOne({"_id": id, 'reportsComplete': {'$exists': False}}, setDict={'reportsComplete': True})

    async def markProductsComplete(self, id: ObjectId):
        await self.db.updateOne({"_id": id}, setDict={'productsComplete': True})

    async def getParentReport(self, id: ObjectId):
        pipeline = [ { '$match': { '_id': id, 'uid': self.db.uid, 'marketplace': self.db.marketplace, 'status': AmazonParentReportTaskStatus.PROCESSING.value } }, { '$lookup': { 'from': 'amazon_child_reports', 'localField': '_id', 'foreignField': 'parent', 'as': 'result' } }, { '$set': { 'progress': { '$let': { 'vars': { 'total': { '$size': '$result' }, 'completed': { '$size': { '$filter': { 'input': '$result', 'as': 'f', 'cond': { '$ne': [ { '$ifNull': [ '$$f.report.filepath', None ] }, None ] } } } } }, 'in': { '$cond': { 'if': { '$eq': [ '$$total', 0 ] }, 'then': 0, 'else': { '$multiply': [ { '$round': [ { '$divide': [ '$$completed', '$$total' ] }, 2 ] }, 100 ] } } } } } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { '$unsetField': { 'input': '$$ROOT', 'field': 'result' } }, { '$arrayToObject': { '$reduce': { 'input': '$result', 'initialValue': [], 'in': { '$let': { 'vars': { 'key': { '$toLower': { '$replaceAll': { 'input': '$$this.reporttype', 'find': '_', 'replacement': '' } } } }, 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.k', '$$key' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ { 'k': '$$key', 'v': [ { '$mergeObjects': [ '$$this.report', { '_id': '$$this._id' } ] } ] } ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.k', '$$key' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'v': { '$concatArrays': [ '$$v.v', [ { '$mergeObjects': [ '$$this.report', { '_id': '$$this._id', 'filepath': '$$this.filepath' } ] } ] ] } } ] } ] } } } ] } } } } } } ] } } } ]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Pending Group Report")
        return AmazonParentReport(**data[0])
        

    async def terminateParent(self, id: str, error):
        await self.db.updateOne({"_id": ObjectId(id)}, setDict={'error': error})

    async def markParentAsCompleted(self, id: str):
        await self.db.updateOne({"_id": ObjectId(id)}, setDict={'status':AmazonParentReportTaskStatus.COMPLETED.value}, markCompletion=True)
