from datetime import datetime
from dzgroshared.db.model import ErrorDetail, StartEndDate
from dzgroshared.db.daily_report_group.model import AmazonParentReport
from dzgroshared.db.daily_report_item.model import  AmazonSpapiReport, AmazonAdReport, AmazonExportReport, AmazonDataKioskReport
from pymongo.collection import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import AmazonParentReportTaskStatus, AmazonReportType, CollectionType
from dzgroshared.client import DzgroSharedClient


class DailyReportItemHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.DAILY_REPORT_ITEM.value), marketplace=self.client.marketplaceId)

    async def addReports(self, reports: dict[AmazonReportType, list[AmazonSpapiReport]|list[AmazonAdReport]|list[AmazonExportReport]|list[AmazonDataKioskReport]], dates: StartEndDate):
        childReports: list[dict] = []
        id = await self.client.db.daily_report_group.insertParentReport(dates)
        for k,v in reports.items(): childReports.extend([{'parent': id, 'reporttype': k.value, "report": x.model_dump(mode="json", exclude_none=True, exclude_defaults=True, by_alias=True)} for x in v])
        await self.db.insertMany(childReports)
        return id

    async def updateParentReportStatus(self, id: ObjectId, status: AmazonParentReportTaskStatus):
        await self.db.updateOne({"_id": id}, setDict={'status': status.value})


    async def deleteChildReports(self, id: str):
        await self.db.deleteMany({"parent": ObjectId(id)})

    async def updateChildReport(self, id: str, data: dict):
        await self.db.updateOne({"_id": ObjectId(id)}, setDict={f'report.{k}': v for k,v in data.items()})

    async def addfilepathToChildReport(self, id:str, filepath: str):
        await self.db.updateOne({"_id": ObjectId(id)}, setDict={'filepath': filepath}, markCompletion=True)

    async def addErrorToChildReport(self, id:str, error: dict):
        await self.db.updateOne({"_id": ObjectId(id)}, setDict={'error': error})

