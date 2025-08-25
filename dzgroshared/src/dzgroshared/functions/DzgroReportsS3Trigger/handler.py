from io import BytesIO, StringIO
import pandas as pd
from bson import ObjectId
from dzgroshared.db.collections.dzgro_reports import DzgroReportHelper
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.dzgro_reports import DzgroReport, DzgroReportType
from dzgroshared.functions.DzgroReportsS3Trigger.models import S3TriggerObject, S3TriggerType, S3FileType
from dzgroshared.models.enums import S3Bucket
from dzgroshared.models.s3 import S3GetObjectModel

class DzgroReportS3TriggerProcessor:
    client: DzgroSharedClient
    reportType: DzgroReportType
    prefix: str
    model: S3TriggerObject
    report: DzgroReport

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event:dict):
        records = event.get('Records',[])
        for record in records:
            self.model = S3TriggerObject(**record)
            self.client.setUid(self.model.uid)
            self.client.setMarketplace(ObjectId(self.model.marketplace))
            self.reportType = DzgroReportType(self.model.reporttype)
            self.prefix = f"{self.model.uid}/{self.model.marketplace}/{self.model.reporttype}/{self.model.reportid}/"
            if self.model.triggerType==S3TriggerType.PUT and self.model.s3.object.filetype==S3FileType.CSV: 
                self.report = await self.client.db.dzgro_reports.getReport(self.model.reportid)
                await self.processCSV(self.model, self.reportType)

    async def collate(self):
        bucket = S3Bucket.DZGRO_REPORTS
        resp = self.client.s3.list_objects_v2(Bucket=bucket, Prefix=self.prefix)
        csv_keys = sorted([key for key in (obj.get("Key") for obj in resp.get("Contents", [])) if key is not None and key.endswith(".csv")])
        if not csv_keys:
            return {"status": "no_csv_files"}
        print(f"Found {len(csv_keys)} CSV parts for Report {self.model.reportid}")
        first_obj = self.client.s3.get_object(S3GetObjectModel(Bucket=bucket, Key=csv_keys[0]))
        first_csv = first_obj["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(first_csv))

        # Read remaining files without header
        for key in csv_keys[1:]:
            obj = self.client.s3.get_object(S3GetObjectModel(Bucket=bucket, Key=key))
            csv_data = obj["Body"].read().decode("utf-8")
            part_df = pd.read_csv(StringIO(csv_data), header=None)
            part_df.columns = df.columns  # align with header order
            df = pd.concat([df, part_df], ignore_index=True)

        if self.report.count == len(df):
            

        # Convert final result to XLSX in memory
        output_buffer = BytesIO()
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        # Save merged XLSX back to S3
        final_key = prefix + "final_output.xlsx"
        s3.put_object(Bucket=bucket, Key=final_key, Body=output_buffer.getvalue())

        print(f"Merged XLSX written to {final_key}")

        return {"status": "success", "output": final_key}


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

    async def addSignedUrl(self, model: S3TriggerObject,  url:str):
        await self.client.db.dzgro_reports.addurl(model.reportid, url)


    async def removeMongoDbEntry(self, model: S3TriggerObject):
        await self.client.db.dzgro_reports.deleteReport(model.reportid)


