from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.client import DbClient
from dzgroshared.models.extras.amazon_daily_report import MarketplaceObjectForReport
from dzgroshared.models.model import PyObjectId
from dzgroshared.models.enums import CollectionType
dateFormat = ["%d.%m.%Y %H:%M:%S %Z","%Y-%m-%dT%H:%M:%S%z","%d.%m.%Y"]

class ReportUtil:
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client

    async def fetchData(self, url: str, zipped: bool) -> str:
        import httpx, gzip
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                if zipped:
                    res = gzip.decompress(response.content)
                    return res.decode("latin-1")
                return response.text
        raise ValueError("URL could not be resolved")

    async def insertToS3(self, key: str, url: str, compressionAlgorithm: bool = False) -> tuple[str, str]:
        path = f'reports/{self.client.uid}/{str(self.client.marketplace)}/{key}'
        from dzgroshared.models.s3 import S3PutObjectModel
        data = await self.fetchData(url, compressionAlgorithm)
        self.client.storage.put_object(
            S3PutObjectModel(Key=path, Body=data, ContentType='application/json')
        )
        return data, path
    
    async def update(self, collection: CollectionType, data: list[dict], synctoken: PyObjectId|None=None, deleteWheereSyncTokenMismatch: bool = True):
        if len(data)>0:
            from pymongo import UpdateOne, InsertOne
            index = {"uid": self.client.uid, "marketplace": self.client.marketplace}
            if synctoken: index.update({"synctoken": synctoken})
            ops = [UpdateOne({"_id": item['_id']}, {"$set": {**index, **item}}, upsert=True ) if "_id" in item else InsertOne({**index, **item}) for item in data]
            from dzgroshared.db.DbUtils import DbManager
            db = DbManager(self.client.db.database.get_collection(collection.value))
            inserted_count, upserted_count, modified_count, deleted_count = await db.bulkWrite(ops)
            print("Inserted: ", inserted_count, " Upserted: ", upserted_count, " Modified: ", modified_count, " Deleted: ", deleted_count)
            if synctoken and deleteWheereSyncTokenMismatch:
                ids = list(map(lambda x: x['_id'], data))
                res = await db.deleteMany({"_id": {"$in": ids}, "synctoken": {"$ne": synctoken}})
                await db.aggregate([{"$match": {"_id": {"$in": ids}}}, { '$unset': "synctoken"}, {"$merge": collection.value}])
    
    
