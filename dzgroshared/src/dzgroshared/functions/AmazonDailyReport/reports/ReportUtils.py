from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.client import DbClient
from dzgroshared.models.extras.amazon_daily_report import MarketplaceObjectForReport
from dzgroshared.models.model import PyObjectId
from dzgroshared.models.enums import CollectionType
dateFormat = ["%d.%m.%Y %H:%M:%S %Z","%Y-%m-%dT%H:%M:%S%z","%d.%m.%Y"]

class ReportUtil:
    client: DzgroSharedClient
    marketplace: MarketplaceObjectForReport

    def __init__(self, client: DzgroSharedClient,  marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace
        self.fnClient = client

    def fetchData(self, url: str, zipped: bool)->str:
        import requests, gzip
        if zipped:
            response = requests.get(url, stream=True)
            if response.status_code==200:
                res = gzip.decompress(response.content)
                return res.decode("latin-1")
        response = requests.get(url)
        if response.status_code==200: return response.text
        raise ValueError("URL could not be resolved")

    def insertToS3(self, key: str, url: str, compressionAlgorithm: bool = False)->tuple[str, str]:
        path = f'reports/{self.marketplace.uid}/{str(self.marketplace.id)}/{key}'
        from dzgroshared.models.s3 import S3PutObjectModel
        data = self.fetchData(url, compressionAlgorithm)
        self.client.storage.put_object(
            S3PutObjectModel(Key=path, Body=data, ContentType='application/json')
        )
        return data, path
    
    async def update(self, client: DbClient, collection: CollectionType, data: list[dict], synctoken: PyObjectId|None=None, deleteWheereSyncTokenMismatch: bool = True):
        if len(data)>0:
            from pymongo import UpdateOne, InsertOne
            ops = []
            for item in data:
                x = {"uid": self.marketplace.uid}
                if '_id' not in item or item['_id']!=self.marketplace: x.update({"marketplace": self.marketplace.id})
                x.update(item)
                if synctoken: x.update({"synctoken": synctoken})
                ops.append(UpdateOne( {"_id": item['_id']}, {"$set": x}, upsert=True )) if "_id" in item else ops.append(InsertOne(x))
            from dzgroshared.db.DbUtils import DbManager
            db = DbManager(self.client.db.database.get_collection(collection.value))
            inserted_count, upserted_count, modified_count, deleted_count = await db.bulkWrite(ops)
            print("Inserted: ", inserted_count, " Upserted: ", upserted_count, " Modified: ", modified_count, " Deleted: ", deleted_count)
            if synctoken and deleteWheereSyncTokenMismatch:
                ids = list(map(lambda x: x['_id'], data))
                res = await db.deleteMany({"_id": {"$in": ids}, "synctoken": {"$ne": synctoken}})
                print("Deleted: ", res)
                await db.aggregate([{"$match": {"_id": {"$in": ids}}}, { '$unset': "synctoken"}, {"$merge": collection.value}])
    
    
