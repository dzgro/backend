from bson import ObjectId
from dzgroshared.models.collections.dzgro_report_types import DzgroReportSpecificationWithProjection
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType, DzgroReportType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import Sort


class DzgroReportTypesHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.client = client
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.DZGRO_REPORT_TYPES))

    async def getReportTypes(self):
        reports = await self.db.find(sort=Sort(field="index", order=1), projectionExc=['projection'])
        return reports

    async def getReportType(self, reporttype: DzgroReportType):
        return DzgroReportSpecificationWithProjection(**await self.db.findOne({ '_id': reporttype }))

    async def getProjection(self, reportType: DzgroReportType):
        return (await self.getReportType(reportType)).projection
    
    async def getSampleReportHeaders(self, reportType: DzgroReportType):
        return list((await self.getProjection(reportType)).keys())
