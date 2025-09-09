from datetime import datetime
from dzgroshared.models.model import ErrorDetail, StartEndDate
from dzgroshared.models.extras.amazon_daily_report import AmazonParentReport, AmazonSpapiReport, AmazonAdReport, AmazonExportReport, AmazonDataKioskReport, AmazonSpapiReportDB
from pymongo.collection import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import AmazonParentReportTaskStatus, AmazonReportType, CollectionType
from dzgroshared.client import DzgroSharedClient

class AmazonDailyReportHelper:
    childDB: DbManager
    groupDB: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.childDB = DbManager(client.db.database.get_collection(CollectionType.AMAZON_CHILD_REPORT.value), marketplace=self.client.marketplaceId)
        self.groupDB = DbManager(client.db.database.get_collection(CollectionType.AMAZON_CHILD_REPORT_GROUP.value), marketplace=self.client.marketplaceId)

    async def insertParentReport(self, reports: dict[AmazonReportType, list[AmazonSpapiReport]|list[AmazonAdReport]|list[AmazonExportReport]|list[AmazonDataKioskReport]], dates: StartEndDate):
        childReports: list[dict] = []
        id = await self.groupDB.insertOne({'status':AmazonParentReportTaskStatus.PROCESSING.value, 'dates': dates.model_dump()}, withUidMarketplace=True)
        for k,v in reports.items(): childReports.extend([{'parent': id, 'reporttype': k.value, "report": x.model_dump(mode="json", exclude_none=True, exclude_defaults=True, by_alias=True)} for x in v])
        await self.childDB.insertMany(childReports)
        return id

    async def updateParentReportStatus(self, id: ObjectId, status: AmazonParentReportTaskStatus):
        await self.childDB.updateOne({"_id": id}, setDict={'status': status.value})

    async def markReportsComplete(self, id: ObjectId):
        await self.groupDB.updateOne({"_id": id, 'reportsComplete': {'$exists': False}}, setDict={'reportsComplete': True})

    async def markProductsComplete(self, id: ObjectId):
        await self.groupDB.updateOne({"_id": id}, setDict={'productsComplete': True})

    async def getParentReport(self, id: ObjectId):
        pipeline = [ { '$match': { '_id': id, 'uid': self.groupDB.uid, 'marketplace': self.groupDB.marketplace, 'status': AmazonParentReportTaskStatus.PROCESSING.value } }, { '$lookup': { 'from': 'amazon_child_reports', 'localField': '_id', 'foreignField': 'parent', 'as': 'result' } }, { '$set': { 'progress': { '$let': { 'vars': { 'total': { '$size': '$result' }, 'completed': { '$size': { '$filter': { 'input': '$result', 'as': 'f', 'cond': { '$ne': [ { '$ifNull': [ '$$f.report.filepath', None ] }, None ] } } } } }, 'in': { '$cond': { 'if': { '$eq': [ '$$total', 0 ] }, 'then': 0, 'else': { '$multiply': [ { '$round': [ { '$divide': [ '$$completed', '$$total' ] }, 2 ] }, 100 ] } } } } } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { '$unsetField': { 'input': '$$ROOT', 'field': 'result' } }, { '$arrayToObject': { '$reduce': { 'input': '$result', 'initialValue': [], 'in': { '$let': { 'vars': { 'key': { '$toLower': { '$replaceAll': { 'input': '$$this.reporttype', 'find': '_', 'replacement': '' } } } }, 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.k', '$$key' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ { 'k': '$$key', 'v': [ { '$mergeObjects': [ '$$this.report', { '_id': '$$this._id' } ] } ] } ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.k', '$$key' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'v': { '$concatArrays': [ '$$v.v', [ { '$mergeObjects': [ '$$this.report', { '_id': '$$this._id', 'filepath': '$$this.filepath' } ] } ] ] } } ] } ] } } } ] } } } } } } ] } } } ]
        data = await self.groupDB.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Pending Group Report")
        return AmazonParentReport(**data[0])
        

    async def terminateParent(self, id: str, error):
        await self.groupDB.updateOne({"_id": ObjectId(id)}, setDict={'error': error})

    async def markParentAsCompleted(self, id: str):
        await self.groupDB.updateOne({"_id": ObjectId(id)}, setDict={'status':AmazonParentReportTaskStatus.COMPLETED.value}, markCompletion=True)


    async def deleteChildReports(self, id: str):
        await self.childDB.deleteMany({"parent": ObjectId(id)})

    async def updateChildReport(self, id: str, data: dict):
        await self.childDB.updateOne({"_id": ObjectId(id)}, setDict={f'report.{k}': v for k,v in data.items()})

    async def addfilepathToChildReport(self, id:str, filepath: str):
        await self.childDB.updateOne({"_id": ObjectId(id)}, setDict={'filepath': filepath}, markCompletion=True)

    async def addErrorToChildReport(self, id:str, error: dict):
        await self.childDB.updateOne({"_id": ObjectId(id)}, setDict={'error': error})

