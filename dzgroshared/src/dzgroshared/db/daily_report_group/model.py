
from datetime import datetime
from dzgroshared.db.daily_report_item.model import AmazonAdExportDB, AmazonAdReportDB, AmazonDailyReportMessages, AmazonDataKioskReportDB, AmazonSpapiReportDB
from dzgroshared.db.model import ItemId, StartEndDate
from pydantic.json_schema import SkipJsonSchema


class AmazonParentReport(ItemId):
    createdat: datetime
    completedat: datetime|SkipJsonSchema[None]=None
    dates: StartEndDate
    spapi: list[AmazonSpapiReportDB] = []
    ad: list[AmazonAdReportDB] = []
    adexport: list[AmazonAdExportDB] = []
    kiosk: list[AmazonDataKioskReportDB] = []
    messages: list[AmazonDailyReportMessages] = []
    progress: float
    productsComplete: bool = False