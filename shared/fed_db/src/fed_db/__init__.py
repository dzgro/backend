from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class FedDbClient:

    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase

    def __init__(self, MONGO_FED_CONNECT_URI: str):
        self.client = AsyncIOMotorClient(MONGO_FED_CONNECT_URI)
        self.db = self.client['dzgro-dev']

    def createReport(self, filename: str,pipeline: list[dict], bucket: str = 'dzgro-reports', format: str = 'parquet'):
        pipeline.append( { '$out': { 's3': { 'bucket': bucket, 'filename': filename, 'format': { 'name': format } } } } )
        return self.db['dzgro_report_data'].aggregate(pipeline)

    