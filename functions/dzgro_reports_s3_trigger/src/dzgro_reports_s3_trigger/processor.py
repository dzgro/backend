from db.collections.dzgro_reports import DzgroReportHelper
from models.collections.dzgro_reports import DzgroReportType
from dzgro_reports_s3_trigger.models import S3TriggerObject, S3TriggerType, S3FileType
from bson.objectid import ObjectId

class DzgroReportS3TriggerProcessor:
    model: S3TriggerObject
    reportType: DzgroReportType
    helper: DzgroReportHelper

    def __init__(self, record: dict) -> None:
        self.model = S3TriggerObject(**record)
        self.reportType = DzgroReportType[self.model.reporttype]
        from dzgrosecrets import SecretManager
        from db import DbClient
        dbClient = DbClient(SecretManager().MONGO_DB_CONNECT_URI)
        self.helper = dbClient.dzgro_reports(self.model.uid, ObjectId(self.model.marketplace))

    async def execute(self):
        if self.model.triggerType==S3TriggerType.PUT:
            if self.model.s3.object.filetype==S3FileType.PARQUET: await self.processParquet()
        else: await self.removeMongoDbEntry()

    async def processParquet(self):
        print(self.model.model_dump())
        import pandas as pd
        import io
        from storage import S3Storage
        s3 = S3Storage()
        print(self.model.s3.object.key)
        from models.s3 import S3GetObjectModel, S3Bucket, S3PutObjectModel
        data = s3.get_object(S3GetObjectModel(Bucket=S3Bucket.REPORTS, Key=self.model.s3.object.key))
        df = pd.read_parquet(io.BytesIO(data), engine='pyarrow')
        from dzgro_reports_s3_trigger import cols as ColumnProcessor
        df = ColumnProcessor.convertDataFrame(df, self.reportType)
        with io.BytesIO() as output:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            data = output.getvalue()
        path = f'{self.model.uid}/{self.model.marketplace}/{self.model.reporttype}/{self.model.reportid}/{self.model.reporttype}.xlsx'
        s3.put_object(S3PutObjectModel(Bucket=S3Bucket.REPORTS, Key=path, Body=data, ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        url = s3.create_signed_url_by_path(path)
        await self.addSignedUrl(url)

    async def addSignedUrl(self, url:str):
        await self.helper.addurl(self.model.reportid, url)


    async def removeMongoDbEntry(self):
        await self.helper.deleteReport(self.model.reportid)
        

