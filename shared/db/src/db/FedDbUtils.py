from bson import ObjectId
from models.enums import FederationCollectionType
from pymongo.collection import Collection
from db.PipelineProcessor import PipelineProcessor

class FedDbManager:
    collection: Collection
    marketplace: ObjectId|None
    uid: str|None
    pp: PipelineProcessor

    def __init__(self, name: FederationCollectionType, marketplace: ObjectId|None=None, uid: str|None=None):
        from app.HelperModules.Db import mongo_db
        self.marketplace = marketplace
        self.uid = uid
        if self.marketplace and self.uid: self.pp = PipelineProcessor(self.marketplace, self.uid)
        mongo_db.connect_to_federation_database()
        self.collection = mongo_db.getFedCollection(name)

    def write(self, filename: str,pipeline: list[dict], bucket: str = 'dzgro-reports', format: str = 'parquet'):
        pipeline.append( { '$out': { 's3': { 'bucket': bucket, 'filename': filename, 'format': { 'name': format } } } } )
        print(pipeline)
        return self.collection.aggregate(pipeline)
    