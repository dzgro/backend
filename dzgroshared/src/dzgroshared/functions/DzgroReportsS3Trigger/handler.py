from email.mime import message
from bson import ObjectId
from dzgroshared.db.collections.dzgro_reports import DzgroReportHelper
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.dzgro_reports import DzgroReportType
from dzgroshared.functions.DzgroReportsS3Trigger.models import S3TriggerObject, S3TriggerType, S3FileType

class DzgroReportS3TriggerProcessor:
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event:dict):
        records = event.get('Records',[])
        for record in records:
            model = S3TriggerObject(**record)
            self.client.setUid(model.uid)
            self.client.setMarketplace(ObjectId(model.marketplace))
            reportType = DzgroReportType[model.reporttype]
            if model.triggerType==S3TriggerType.PUT:
                if model.s3.object.filetype==S3FileType.PARQUET: await self.processParquet(model, reportType)
            else: await self.removeMongoDbEntry(model)

    async def processParquet(self, model: S3TriggerObject, reportType: DzgroReportType):
        print(model.model_dump())
        import pandas as pd
        import io
        print(model.s3.object.key)
        from dzgroshared.models.s3 import S3GetObjectModel, S3Bucket, S3PutObjectModel
        data = self.client.storage.get_object(S3GetObjectModel(Bucket=S3Bucket.REPORTS, Key=model.s3.object.key))
        df = pd.read_parquet(io.BytesIO(data), engine='pyarrow')
        from dzgroshared.functions.DzgroReportsS3Trigger import cols as ColumnProcessor
        df = ColumnProcessor.convertDataFrame(df, reportType)
        with io.BytesIO() as output:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            data = output.getvalue()
        path = f'{model.uid}/{model.marketplace}/{model.reporttype}/{model.reportid}/{model.reporttype}.xlsx'
        self.client.storage.put_object(S3PutObjectModel(Bucket=S3Bucket.REPORTS, Key=path, Body=data, ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        url = self.client.storage.create_signed_url_by_path(path)
        await self.addSignedUrl(model, url)

    async def addSignedUrl(self, model: S3TriggerObject,  url:str):
        await self.client.db.dzgro_reports.addurl(model.reportid, url)


    async def removeMongoDbEntry(self, model: S3TriggerObject):
        await self.client.db.dzgro_reports.deleteReport(model.reportid)


