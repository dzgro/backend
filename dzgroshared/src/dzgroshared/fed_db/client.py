from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.enums import S3Bucket
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

class FedDbClient:
    client: DzgroSharedClient
    collection: AsyncIOMotorCollection

    def __init__(self, client: DzgroSharedClient):
        self.client = client
        self.collection = AsyncIOMotorClient(client.secrets.MONGO_DB_FED_CONNECT_URI)['dzgro'][f'dzgro_reports_data_{self.client.env.value.lower()}']
        

    async def createReport(self, filename: str, pipeline: list[dict], bucket: S3Bucket, format: str = 'csv'):
        bucketName = self.client.storage.getBucketName(bucket)
        pipeline.append( { '$out': { 's3': { 'bucket': bucketName, 'filename': filename, 'format': { 'name': format } } } } )
        return await self.collection.aggregate(pipeline).to_list()

    