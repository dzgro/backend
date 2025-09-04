from datetime import datetime, timedelta
from bson import ObjectId
from dzgroshared.db.collections.pipelines.queries import GetQueries
from dzgroshared.models.collections.queries import QueryList, Query
from dzgroshared.models.enums import CollateType, CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import StartEndDate

class QueryHelper:
    client: DzgroSharedClient
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.client = client
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.QUERIES))

    async def getQueries(self) -> QueryList:
        pipeline = GetQueries.pipeline(self.uid, self.marketplace)
        data = await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)
        return QueryList(queries=[Query(**item) for item in data])

    async def buildQueries(self, dates: StartEndDate):
        pipeline = GetQueries.pipeline(self.uid, self.marketplace, dates)
        pipeline.extend([{"$project": {"tag": 0, "dates": 0}}, {"$match": {"disabled": False}},{"$set": {"collatetype": CollateType.list()}}, {"$unwind": "$collatetype"}])
        pipeline.append({ "$addFields": { "currdates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$curr.startdate", "endDate": "$curr.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$curr.startdate", "unit": "day", "amount": "$$i" } } } }, "predates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$pre.startdate", "endDate": "$pre.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$pre.startdate", "unit": "day", "amount": "$$i" } } } } } } )
        pipeline.append({ '$lookup': { 'from': 'date_analytics', 'let': { 'currdates': '$currdates','predates': '$predates', 'collatetype': "$collatetype", 'dates': {"$setUnion": {"$concatArrays": ["$currdates","$predates"]}} }, 'pipeline': [ { '$match': { '$expr': { '$and': [ {"$eq": ["$uid", self.uid]},{"$eq": ["$marketplace", self.marketplace]},{"$eq": ["$collatetype", "$$collatetype"]},{ '$in': [ '$date', '$$dates' ] } ] } } }, { '$group': { '_id': { 'collatetype': '$collatetype', 'value': '$value', 'parent': '$parent' }, 'data': { '$push': '$$ROOT' } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { '$reduce': { 'input': '$data', 'initialValue': { 'curr': [], 'pre': [] }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$in': [ '$$this.date', "$$currdates" ] }, 'then': { 'curr': { '$concatArrays': [ '$$value.curr', [ '$$this.data' ] ] } }, 'else': { '$cond': { 'if': { '$in': [ '$$this.date', "$$predates" ] }, 'then': { 'pre': { '$concatArrays': [ '$$value.pre', [ '$$this.data' ] ] } }, 'else': {} } } } } ] } } } ] } } }, { '$set': { 'curr': { '$reduce': { 'input': '$curr', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } }, 'pre': { '$reduce': { 'input': '$pre', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } } } } ], 'as': 'data' } })
        pipeline.extend([{ '$unwind': { 'path': '$data', 'preserveNullAndEmptyArrays': False } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$data', { 'queryid': '$_id' } ] } } }])
        from dzgroshared.db.collections.pipelines.queries import QueryBuilder
        pipeline.append(QueryBuilder.addMissingFields('curr'))
        pipeline.extend(QueryBuilder.addDerivedMetrics('curr'))
        pipeline.extend(QueryBuilder.build_transformation_pipeline(True, 'curr'))
        pipeline.append(QueryBuilder.addMissingFields('pre'))
        pipeline.extend(QueryBuilder.addDerivedMetrics('pre'))
        pipeline.extend(QueryBuilder.build_transformation_pipeline(True, 'pre'))
        pipeline.append(QueryBuilder.addGrowth())
        pipeline.append(QueryBuilder.create_comparison_data())
        pipeline.append({"$set": {"uid": self.uid, "marketplace": self.marketplace}})
        pipeline.extend([{"$project": {"curr": 0, "pre": 0,'growth':0}}, {"$merge": {"into":CollectionType.QUERY_RESULTS.value, "whenMatched": "merge", "whenNotMatched": "insert"}}])
        await self.client.db.query_results.deleteQueryResults()
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        await self.client.db.marketplaces.marketplaceDB.aggregate(pipeline)
