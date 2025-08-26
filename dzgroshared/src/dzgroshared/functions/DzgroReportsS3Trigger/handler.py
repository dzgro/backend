from io import BytesIO, StringIO
import pandas as pd
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.dzgro_reports import DzgroReport, DzgroReportType
from dzgroshared.functions.DzgroReportsS3Trigger.models import S3TriggerObject, S3TriggerType, S3FileType
from dzgroshared.models.enums import S3Bucket
from dzgroshared.models.s3 import S3GetObjectModel, S3PutObjectModel

class DzgroReportS3TriggerProcessor:
    client: DzgroSharedClient
    reportType: DzgroReportType
    prefix: str
    model: S3TriggerObject
    report: DzgroReport
    bucket: S3Bucket = S3Bucket.DZGRO_REPORTS

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event:dict, data: list[dict]|None=None):
        records = event.get('Records',[])
        for record in records:
            try:
                self.model = S3TriggerObject(**record)
                self.client.setUid(self.model.uid)
                self.client.setMarketplace(ObjectId(self.model.marketplace))
                self.reportType = DzgroReportType(self.model.reporttype)
                self.prefix = f"{self.model.uid}/{self.model.marketplace}/{self.model.reporttype}/{self.model.reportid}/"
                if data is not None: 
                    df = pd.DataFrame(data)
                    await self.createExcel(df)
                elif self.model.triggerType==S3TriggerType.PUT and self.model.s3.object.filetype==S3FileType.CSV: 
                    self.report = await self.client.db.dzgro_reports.getReport(self.model.reportid)
                    df = await self.processCSV(self.model, self.reportType)
                    if df: await self.createExcel(df)
            except Exception as e:
                print(e)

    async def collate(self):
        resp = self.client.s3.list_objects_v2(Bucket=self.bucket, Prefix=self.prefix)
        csv_keys = sorted([key for key in (obj.get("Key") for obj in resp.get("Contents", [])) if key is not None and key.endswith(".csv")])
        if not csv_keys: return None
        print(f"Found {len(csv_keys)} CSV parts for Report {self.model.reportid}")
        first_obj = self.client.s3.get_object(S3GetObjectModel(Bucket=self.bucket, Key=csv_keys[0]))
        first_csv = first_obj["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(first_csv))
        for key in csv_keys[1:]:
            obj = self.client.s3.get_object(S3GetObjectModel(Bucket=self.bucket, Key=key))
            csv_data = obj["Body"].read().decode("utf-8")
            part_df = pd.read_csv(StringIO(csv_data), header=None)
            part_df.columns = df.columns  # align with header order
            df = pd.concat([df, part_df], ignore_index=True)
        count = len(df)
        return df if self.report.count == count else None

    async def createExcel(self, df: pd.DataFrame):
        output_buffer = BytesIO()
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        final_key = f'{self.prefix}{self.reportType.value}.xlsx'
        req = S3PutObjectModel(Bucket=self.bucket, Key=final_key, ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.client.s3.put_object(req, Body=output_buffer.getvalue())
        await self.client.db.dzgro_reports.addKey(self.model.reportid, final_key)
        return final_key


    async def processCSV(self, model: S3TriggerObject, reportType: DzgroReportType):
        print(model.model_dump())
        import pandas as pd
        import io
        print(model.s3.object.key)
        from dzgroshared.models.s3 import S3GetObjectModel, S3Bucket, S3PutObjectModel
        bucket = S3Bucket.DZGRO_REPORTS
        stream = self.client.storage.get_object(S3GetObjectModel(Bucket=bucket, Key=model.s3.object.key))['Body']
        df = pd.read_parquet(io.BytesIO(stream.read()), engine='pyarrow')
        from dzgroshared.functions.DzgroReportsS3Trigger import cols as ColumnProcessor
        df = ColumnProcessor.convertDataFrame(df, reportType)
        with io.BytesIO() as output:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            data = output.getvalue()
        path = f'{model.uid}/{model.marketplace}/{model.reporttype}/{model.reportid}/{model.reporttype}.xlsx'
        self.client.storage.put_object(S3PutObjectModel(Bucket=bucket, Key=path, Body=data, ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        url = self.client.storage.create_signed_url_by_path(path, bucket)
        await self.addSignedUrl(model, url)

