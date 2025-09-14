from bson import ObjectId
from dzgroshared.db.dzgro_report_types.model import DzgroReportSpecificationWithProjection
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollateType, CollectionType, DzgroReportType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.model import Sort


class DzgroReportTypesHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.DZGRO_REPORT_TYPES))

    async def getReportTypes(self):
        reports = await self.db.find(sort=Sort(field="index", order=1), projectionExc=['projection'])
        return reports

    async def getReportType(self, reporttype: DzgroReportType):
        return DzgroReportSpecificationWithProjection(**await self.db.findOne({ '_id': reporttype }))

    async def getProjection(self, reportType: DzgroReportType, collatetype: CollateType|None=None):
        projections = (await self.getReportType(reportType)).projection
        if reportType in [DzgroReportType.KEY_METRICS] and collatetype==CollateType.SKU:
            keys_to_remove = [ "Sessions", "Browser Sessions", "Browser Sessions %", "Mobile App Sessions", "Mobile App Sessions &", "Unit Session %", "Page Views", "Browser Page Views", "Browser Page Views %", "Mobile App Page Views", "Mobile App Page Views %", "Buy Box %" ]
            projections =  {k: v for k, v in projections.items() if k not in keys_to_remove}
        return projections

    
    async def getSampleReportHeaders(self, reportType: DzgroReportType, collatetype: CollateType|None=None):
        return list((await self.getProjection(reportType, collatetype)).keys())
