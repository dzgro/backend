from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.enums import CollectionType
from dzgroshared.storage.model import S3Bucket
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

class FedDbClient:
    client: DzgroSharedClient
    collection: AsyncIOMotorCollection

    def __init__(self, client: DzgroSharedClient):
        try:
            self.client = client        
            print("Connecting to Fed MongoDB...", self.client.DB_NAME)
            self.collection = self.client.mongoFedClient[self.client.DB_NAME].get_collection(CollectionType.DZGRO_REPORT_DATA.value)
        except Exception as e:
            print(f"Error connecting to Fed MongoDB: {e}")

    async def createReport(self, filename: str, pipeline: list[dict], bucket: S3Bucket, format: str = 'csv'):
        bucketName = self.client.storage.getBucketName(bucket)
        pipeline.append( { '$out': { 's3': { 'bucket': bucketName, 'filename': filename, 'format': { 'name': format } } } } )
        return await self.collection.aggregate(pipeline).to_list(length=None)