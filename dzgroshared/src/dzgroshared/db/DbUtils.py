from datetime import datetime, timezone
from typing import Any
from dzgroshared.db.model import PyObjectId, Sort
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from dzgroshared.db.PipelineProcessor import PipelineProcessor
import time

class DbManager:
    collection: AsyncIOMotorCollection
    marketplace: ObjectId
    uid: str
    pp: PipelineProcessor

    def __init__(self, collection: AsyncIOMotorCollection, uid: str|None=None, marketplace: ObjectId|str|PyObjectId|None=None):
        if(marketplace): self.marketplace = marketplace if isinstance(marketplace, ObjectId) else ObjectId(str(marketplace))
        if uid: self.uid = uid
        self.pp = PipelineProcessor(uid, marketplace)
        self.collection = collection

    
    def __getattr__(self, name):
        return None
    
    def convertToObjectId(self, id: str|ObjectId):
        return ObjectId(id) if isinstance(id, str) else id

    async def aggregate(self, pipeline: list[dict])->list[dict]:
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        start_time = time.perf_counter()
        try:
            result = self.collection.aggregate(pipeline)
            data = await result.to_list()
            process_time_seconds = (time.perf_counter() - start_time)  # ms
            print(f"Aggregation took {process_time_seconds:.4f} seconds")
            return data
        except Exception as e:
            print(e)
            return []

    async def distinct(self, fieldname:str, filters: dict = {}):
        # print(pipeline)
        return await self.collection.distinct(fieldname, self.getFilterDict(filters))
    
    def addUidMarketplaceToDict(self, data: dict):
        obj = {}
        if self.uid: obj['uid'] = self.uid
        if self.marketplace: obj['marketplace'] = str(self.marketplace)
        obj.update(data)
        return obj
    
    def getFilterDict(self, filterDict: dict)->dict:
        if "_id" in filterDict: return filterDict
        if self.uid and 'uid' not in filterDict and self.uid not in filterDict.values(): filterDict.update({"uid": self.uid})
        if self.marketplace and 'marketplace' not in filterDict and self.marketplace not in filterDict.values(): filterDict.update({"marketplace": self.marketplace})
        return filterDict
    
    def getProjectionDict(self, projectionInc: list[str], projectionExc: list[str])->dict|None:
        if (projectionInc+projectionExc): return {**{k: 0 for k in projectionExc}, **{k: 1 for k in projectionInc}}

    def getFilterAndProjection(self, filterDict: dict, projectionInc: list[str], projectionExc: list[str], withUidMarketplace)->tuple[dict, dict|None]:
        if not withUidMarketplace: return filterDict, self.getProjectionDict(projectionInc, projectionExc)
        return self.getFilterDict(filterDict), self.getProjectionDict(projectionInc, projectionExc)

    async def findOne(self, filterDict: dict = {}, projectionInc: list[str] = [], projectionExc: list[str] = [], withUidMarketplace = True)->dict:
        filterDict, projection = self.getFilterAndProjection(filterDict, projectionInc, projectionExc, withUidMarketplace = withUidMarketplace)
        if projection: res = await self.collection.find_one(filterDict, projection)
        else: res = await self.collection.find_one(filterDict)
        if not res: raise ValueError("Not Found")
        return res
    
    async def find(self, filterDict: dict = {}, projectionInc: list[str] = [], projectionExc: list[str] = [], limit: int|None=None, skip: int|None=None, sort: Sort|None=None, withUidMarketplace = True)->list[dict]:
        try:
            filterDict, projection = self.getFilterAndProjection(filterDict, projectionInc, projectionExc, withUidMarketplace = withUidMarketplace)
            res = self.collection.find(filter=filterDict, projection=projection)
            if sort: res = res.sort(sort.field, sort.order)
            if skip: res = res.skip(skip)
            if limit: res = res.limit(limit)
            return await res.to_list()
        except Exception as e:
            raise ValueError(e.args[0])
    
    async def insertMany(self, data: list[dict])->list[ObjectId]:
        data = [self.getFilterDict(item) for item in data]
        return (await self.collection.insert_many(data)).inserted_ids
    
    async def insertOne(self, data: dict, timestamp:bool=True, timestampKey: str="createdat")->PyObjectId:
        if timestamp: data.update({timestampKey: datetime.now(timezone.utc)})
        data.update(self.getFilterDict(data))
        try: return PyObjectId((await self.collection.insert_one(data)).inserted_id)
        except Exception as e:
            raise ValueError("Could not insert")
        
    
    async def deleteMany(self, filterDict: dict = {})->int:
        filterDict = self.getFilterDict(filterDict)
        return (await self.collection.delete_many(filterDict)).deleted_count
    
    async def deleteOne(self, filterDict: dict = {})->int:
        filterDict = self.getFilterDict(filterDict)
        return (await self.collection.delete_one(filterDict)).deleted_count
    
    async def updateOne(self, filterDict: dict = {}, setDict: dict = {}, unsetFields: list[str]=[], upsert: bool = False, markCompletion: bool=False)->tuple[int, ObjectId|str|None]:
        filterDict = self.getFilterDict(filterDict)
        if markCompletion: setDict.update({"completedat": datetime.now(timezone.utc)})
        result = await self.collection.update_one(filterDict, {"$set": setDict, "$unset": {f: "" for f in unsetFields}}, upsert=upsert)
        return result.modified_count, result.upserted_id
    

    async def findOneAndUpdate(self, filterDict: dict = {}, setDict: dict = {})->dict:
        filterDict = self.getFilterDict(filterDict)
        return await self.collection.find_one_and_update(filterDict, {"$set": setDict}, return_document=True)
    
    
    
    async def incOne(self, filterDict: dict = {}, incDict: dict = {})->tuple[int, ObjectId|None]:
        filterDict = self.getFilterDict(filterDict)
        result = await self.collection.update_one(filterDict, {"$inc": incDict})
        return result.modified_count, result.upserted_id
    
    async def updateMany(self, filterDict: dict = {}, setDict: dict = {})->int:
        filterDict = self.getFilterDict(filterDict)
        return (await self.collection.update_many(filterDict, {"$set": setDict})).modified_count
    
    async def deleteFields(self, fields: list[str], filterDict: dict = {})->int:
        unsetDict = {"$unset": {f: "" for f in fields}}
        filterDict = self.getFilterDict(filterDict)
        return (await self.collection.update_many(filterDict, unsetDict)).modified_count
    
    async def count(self, filterDict: dict = {})->int:
        filterDict = self.getFilterDict(filterDict)
        return await self.collection.count_documents(filterDict)
    
    async def bulkWrite(self, operations: list[Any])->Any:
        res = await self.collection.bulk_write(operations)
        return res.inserted_count, res.upserted_count, res.modified_count, res.deleted_count
    

