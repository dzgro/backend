from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.models.amazonapi.spapi.reports import SPAPICreateReportSpecification

class SPAPIReportsHelper:
    dbManager: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.dbManager = DbManager(client.db.database.get_collection(CollectionType.SPAPI_REPORTS.value), uid=client.uid, marketplace=client.marketplace)

    async def createReport(self, req: SPAPICreateReportSpecification):
        id = await self.dbManager.insertOne(
            {"req": req.model_dump(exclude_none=True)}
        )
        self.client.sqs.sendMessage

    async def addToS3(self, reportid: str, subscriptionid:str):
        await self.dbManager.insertOne(
            {"reportId": reportid, "subscriptionid": subscriptionid}
        )

    