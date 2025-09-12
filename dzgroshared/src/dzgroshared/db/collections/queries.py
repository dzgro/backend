from datetime import datetime, timedelta
from bson import ObjectId
from dzgroshared.db.collections.pipelines.queries import GetQueries
from dzgroshared.models.collections.analytics import SingleMetricPeriodDataRequest
from dzgroshared.models.collections.queries import QueryList, Query
from dzgroshared.models.enums import CollateType, CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.model import StartEndDate

class QueryHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.QUERIES))

    async def getQueries(self) -> QueryList:
        pipeline = GetQueries.pipeline(self.client.marketplaceId)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        return QueryList(queries=[Query(**item) for item in data])
    
    async def getQueryTable(self, req: SingleMetricPeriodDataRequest):
        lookupLet = { 'marketplace': self.client.marketplaceId, 'queryid': '$_id', 'collatetype': 'marketplace' }
        if req.value: lookupLet['value'] = req.value
        lookupMatch = { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$eq': [ '$queryid', '$$queryid' ] }, { '$eq': [ '$collatetype', '$$collatetype' ] } ] } }
        if req.value: lookupMatch['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
        pipeline = [ { '$match': { 'uid': { '$exists': False } } }, { '$lookup': { 'from': 'query_results', 'let': lookupLet, 'pipeline': [ { '$match': lookupMatch }, { '$project': { 'data': 1, '_id': 0 } } ], 'as': 'data' } }, { '$set': { 'data': { '$first': '$data.data' } } } ]
        pipeline.extend([{"$match": { "data": {"$exists": True}}}, { '$project': { 'tag': 1, f'data.{req.key.value}': 1, "_id":0 } }])
        data = await self.db.aggregate(pipeline)
        from dzgroshared.db.extras import Analytics
        data = Analytics.transformCurrPreData(data, self.client.marketplace.countrycode)
        return data
    
