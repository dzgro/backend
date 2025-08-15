from dzgroshared.client import DzgroSharedClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class FedDbClient:
    db: AsyncIOMotorDatabase

    def __init__(self, client: DzgroSharedClient):
        self.db = AsyncIOMotorClient(client.secrets.MONGO_DB_FED_CONNECT_URI)[client.env.value]
        

    def createReport(self, filename: str,pipeline: list[dict], bucket: str = 'dzgro-reports', format: str = 'parquet'):
        pipeline.append( { '$out': { 's3': { 'bucket': bucket, 'filename': filename, 'format': { 'name': format } } } } )
        return self.db['dzgro_report_data'].aggregate(pipeline)

    