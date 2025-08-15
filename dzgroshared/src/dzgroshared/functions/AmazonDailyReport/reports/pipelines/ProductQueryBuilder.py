from datetime import timedelta, datetime

from bson import ObjectId
from dzgroshared.db.client import DbClient
from dzgroshared.db.DataTransformer import Datatransformer
from dzgroshared.db.collections.queries import QueryHelper
from dzgroshared.models.collections.queries import Query, QueryPeriod
from dzgroshared.models.enums import CollateTypeTag, CollectionType
from dzgroshared.models.extras.amazon_daily_report import AmazonParentReport, MarketplaceObjectForReport, QueryBuilderValue

class QueryBuilder:
    dbClient: DbClient
    marketplace: MarketplaceObjectForReport
    report: AmazonParentReport

    def __init__(self, dbClient: DbClient, marketplace: MarketplaceObjectForReport, report: AmazonParentReport):
        self.marketplace = marketplace
        self.report = report
        self.dbClient = dbClient

    def get_month_datetimes_till(self, date_input: datetime) -> list[datetime]:
        first_day = date_input.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        delta = date_input.date() - first_day.date()
        return [first_day + timedelta(days=i) for i in range(delta.days + 1)]
    
    def get_prev_month_datetimes_till_same_day(self, date_input: datetime) -> list[datetime]:
        last_day_prev_month = date_input.replace(day=1) - timedelta(days=1)
        day_limit = min(date_input.day, last_day_prev_month.day)
        start_day = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return [start_day + timedelta(days=i) for i in range(day_limit)]
    
    def get_all_dates_of_prev_month(self, date_input: datetime) -> list[datetime]:
        last_day_prev_month = date_input.replace(day=1) - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        days_in_month = last_day_prev_month.day
        return [first_day_prev_month + timedelta(days=i) for i in range(days_in_month)]

    async def getTags(self):
        data = await self.dbClient.queries.db.find({"marketplace": {"$exists": False}})
        return [QueryBuilderValue(tag=CollateTypeTag(item['tag']), _id=item["_id"]) for item in data]


    def getQuery(self, query: QueryBuilderValue)->Query|None:
        if query.tag==CollateTypeTag.DAYS_7:
            return Query(_id=query.id, tag=query.tag, 
                  curr=QueryPeriod(start=self.report.enddate-timedelta(days=6), end=self.report.enddate, label=''),
                  pre=QueryPeriod(start=self.report.enddate-timedelta(days=13), end=self.report.enddate-timedelta(days=7), label='')
                  )
        elif query.tag==CollateTypeTag.DAYS_30:
            return Query(_id=query.id, tag=query.tag,
                  curr=QueryPeriod(start=self.report.enddate-timedelta(days=29), end=self.report.enddate, label=''),
                  pre=QueryPeriod(start=self.report.enddate-timedelta(days=59), end=self.report.enddate-timedelta(days=30), label='')
                  )
        elif query.tag==CollateTypeTag.MONTH_ON_NONTH:
            currdates = self.get_month_datetimes_till(self.report.enddate)
            preDates = self.get_prev_month_datetimes_till_same_day(self.report.enddate)
            return Query(_id=query.id, tag=query.tag,
                  curr=QueryPeriod(start=currdates[0], end=currdates[-1], label=''),
                  pre=QueryPeriod(start=preDates[0], end=preDates[-1], label=''),
                  )
        elif query.tag==CollateTypeTag.MONTH_OVER_MONTH:
            currdates = self.get_month_datetimes_till(self.report.enddate)
            preDates = self.get_all_dates_of_prev_month(self.report.enddate)
            return Query(_id=query.id, tag=query.tag,
                  curr=QueryPeriod(start=currdates[0], end=currdates[-1], label=''),
                  pre=QueryPeriod(start=preDates[0], end=preDates[-1], label=''),
                  )
        else: return None

    async def getNextQuery(self, query: Query|None):
        allTags = await self.getTags()
        if not query: return self.getQuery(allTags[-1])
        index = next((i for i, x in enumerate(allTags) if x.tag==query.tag), None)
        if not index or index==0: return None
        return self.getQuery(allTags[index-1])

    async def execute(self, query: Query):
        matchStage = {"$match": {"_id": query.id}}
        setDates = {"$set": {"curr": {"start": query.curr.start, "end": query.curr.end}, "pre": {"start": query.pre.start, "end": query.pre.end}}}
        createDates = { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$arrayToObject': { '$reduce': { 'input': [ 'curr', 'pre' ], 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this', 'v': { '$let': { 'vars': { 'item': { '$getField': { 'input': '$$ROOT', 'field': '$$this' } } }, 'in': { '$reduce': { 'input': { '$range': [ 0, {"$sum": [{ '$dateDiff': { 'startDate': '$$item.start', 'endDate': '$$item.end', 'unit': 'day' } },1]}, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateAdd': { 'startDate': '$$item.start', 'unit': 'day', 'amount': '$$this' } } ] ] } } } } } } ] ] } } } } ] } } }
        lookupAnalytics = { '$lookup': { 'from': 'date_analytics', 'let': { 'uid': self.marketplace.uid, 'marketplace': self.marketplace.id, 'dates': { '$setUnion': [ '$curr', '$pre' ] } }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$in': [ '$date', '$$dates' ] } ] } } }, { "$project": { "_id": 0 } } ], 'as': 'data' } }
        setData = { '$set': { 'data': { '$reduce': { 'input': '$data', 'initialValue': [], 'in': { '$let': { 'vars': { 'key': { '$concat': [ '$$this.collatetype', { '$toString': '$$this.value' } ] }, 'date': '$$this.date', 'item': '$$this', 'sales': { '$cond': { 'if': { '$eq': [ { '$ifNull': [ '$$this.sales', None ] }, None ] }, 'then': [], 'else': [ '$$this.sales' ] } }, 'ad': { '$cond': { 'if': { '$eq': [ { '$ifNull': [ '$$this.ad', None ] }, None ] }, 'then': [], 'else': [ '$$this.ad' ] } }, 'traffic': { '$cond': { 'if': { '$eq': [ { '$ifNull': [ '$$this.traffic', None ] }, None ] }, 'then': [], 'else': [ '$$this.traffic' ] } } }, 'in': { '$cond': { 'if': { '$eq': [ { '$indexOfArray': [ '$$value.key', '$$key' ] }, -1 ] }, 'then': { '$concatArrays': [ '$$value', [ { '$mergeObjects': [ { 'key': '$$key' }, { '$arrayToObject': { '$filter': { 'input': { '$objectToArray': '$$this' }, 'as': 'kv', 'cond': { '$not': { '$in': [ '$$kv.k', [ 'ad', 'sales', 'traffic' ] ] } } } } }, { '$arrayToObject': { '$reduce': { 'input': [ 'curr', 'pre' ], 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this', 'v': { '$let': { 'vars': { 'isdate': { '$in': [ '$$date', { '$getField': { 'input': '$$ROOT', 'field': '$$this' } } ] } }, 'in': { '$arrayToObject': { '$reduce': { 'input': [ 'sales', 'ad', 'traffic' ], 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this', 'v': { '$cond': { 'if': '$$isdate', 'then': { '$let': { 'vars': { 'val': { '$getField': { 'input': '$$item', 'field': '$$this' } } }, 'in': { '$cond': { 'if': { '$eq': [ { '$ifNull': [ '$$val', None ] }, None ] }, 'then': [], 'else': [ '$$val' ] } } } }, 'else': [] } } } ] ] } } } } } } } ] ] } } } } ] } ] ] }, 'else': { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': { 'if': { '$ne': [ '$$v.key', '$$key' ] }, 'then': '$$v', 'else': { '$mergeObjects': [ '$$v', { '$cond': { 'if': { '$in': [ '$$date', '$curr' ] }, 'then': { 'curr': { 'sales': { '$concatArrays': [ '$$v.curr.sales', '$$sales' ] }, 'ad': { '$concatArrays': [ '$$v.curr.ad', '$$ad' ] }, 'traffic': { '$concatArrays': [ '$$v.curr.traffic', '$$traffic' ] } } }, 'else': {} } }, { '$cond': { 'if': { '$in': [ '$$date', '$pre' ] }, 'then': { 'pre': { 'sales': { '$concatArrays': [ '$$v.pre.sales', '$$sales' ] }, 'ad': { '$concatArrays': [ '$$v.pre.ad', '$$ad' ] }, 'traffic': { '$concatArrays': [ '$$v.pre.traffic', '$$traffic' ] } } }, 'else': {} } } ] } } } } } } } } } } } } }
        pipeline = [matchStage, setDates, createDates, lookupAnalytics, setData]
        dt = Datatransformer(self.dbClient.queries.db.pp)
        pipeline.extend(dt.addAnalyticKeys())
        pipeline.extend([{ '$unwind': { 'path': '$data' } }, {"$replaceRoot": { "newRoot": { "$mergeObjects": [ "$$ROOT", "$data" ] } }}])
        createCurrPreObjects = { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$arrayToObject': { '$reduce': { 'input': [ 'curr', 'pre' ], 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this', 'v': { '$let': { 'vars': { 'data': { '$getField': { 'input': '$$ROOT', 'field': '$$this' } } }, 'in': { '$arrayToObject': { '$reduce': { 'input': [ 'sales', 'ad', 'traffic' ], 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$let': { 'vars': { 'cData': { '$getField': { 'input': '$$data', 'field': '$$this' } } }, 'in': { '$reduce': { 'input': '$$cData', 'initialValue': [], 'in': { '$let': { 'vars': { 'val': '$$value', 'curr': { '$objectToArray': '$$this' } }, 'in': { '$reduce': { 'input': '$$curr', 'initialValue': '$$val', 'in': { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.k', '$$this.k' ] }, -1 ] }, { '$concatArrays': [ '$$value', [ '$$this' ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.k', '$$this.k' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'v': { '$sum': [ '$$v.v', '$$this.v' ] } } ] } ] } } } ] } } } } } } } } } ] } } } } } } } ] ] } } } } ] } } }
        addCalculatedFields = { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { '$arrayToObject': { '$reduce': { 'input': [ 'curr', 'pre' ], 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$this', 'v': { '$let': { 'vars': { 'data': { '$getField': { 'input': '$$ROOT', 'field': '$$this' } } }, 'in': { '$reduce': { 'input': '$allkeys', 'initialValue': '$$data', 'in': { '$cond': [ { '$not': { '$in': [ '$$this.value', '$calculatedkeys' ] } }, '$$value', { '$mergeObjects': [ '$$value', { '$let': { 'vars': { 'key': '$$this', 'val': '$$value', 'num': { '$getField': { 'input': '$$value', 'field': { '$arrayElemAt': [ '$$this.subkeys', 0 ] } } }, 'denom': { '$getField': { 'input': '$$value', 'field': { '$arrayElemAt': [ '$$this.subkeys', 1 ] } } } }, 'in': { '$cond': [ { '$and': [ { '$ne': [ { '$ifNull': [ '$$num', None ] }, None ] }, { '$ne': [ { '$ifNull': [ '$$denom', None ] }, None ] } ] }, { '$arrayToObject': [ [ { 'k': '$$key.value', 'v': { '$let': { 'vars': { 'isPercent': '$$key.isPercent', 'isDivide': { '$eq': [ '$$key.operation', 'divide' ] }, 'isAdd': { '$eq': [ '$$key.operation', 'add' ] }, 'isSubtract': { '$eq': [ '$$key.operation', 'subtract' ] } }, 'in': { '$cond': [ '$$isAdd', { '$sum': [ '$$num', '$$denom' ] }, { '$cond': [ '$$isSubtract', { '$subtract': [ '$$num', '$$denom' ] }, { '$cond': [ { '$eq': [ '$$denom', 0 ] }, 0, { '$multiply': [ { '$divide': [ '$$num', '$$denom' ] }, { '$cond': [ '$$isPercent', 100, 1 ] } ] } ] } ] } ] } } } } ] ] }, {} ] } } } ] } ] } } } } } } ] ] } } } } ] } } }
        addCurrPre = { '$set': { 'data': { '$reduce': { 'input': '$allkeys', 'initialValue': {}, 'in': { '$mergeObjects': [ '$$value', { '$let': { 'vars': { 'field': '$$this.value' }, 'in': { '$let': { 'vars': { 'curr': { '$ifNull': [ { '$getField': { 'input': '$curr', 'field': '$$field' } }, None ] }, 'pre': { '$ifNull': [ { '$getField': { 'input': '$pre', 'field': '$$field' } }, None ] } }, 'in': { '$cond': { 'if': { '$or': [ { '$ne': [ '$$curr', None ] }, { '$ne': [ '$$pre', None ] } ] }, 'then': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': '$$field', 'v': { '$mergeObjects': [ { '$cond': { 'if': { '$ne': [ '$$curr', None ] }, 'then': { 'curr': '$$curr' }, 'else': {} } }, { '$cond': { 'if': { '$ne': [ '$$pre', None ] }, 'then': { 'pre': '$$pre' }, 'else': {} } } ] } } ] ] } ] }, 'else': '$$value' } } } } } } ] } } } } }
        addGrowth = { '$set': { 'data': { '$arrayToObject': { '$reduce': { 'input': '$allkeys', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$in': [ '$$this.value', '$querykeys' ] }, { '$let': { 'vars': { 'data': { '$let': { 'vars': { 'ck': { '$getField': { 'input': '$curr', 'field': '$$this.value' } }, 'pk': { '$getField': { 'input': '$pre', 'field': '$$this.value' } } }, 'in': { '$cond': [ { '$and': [ { '$eq': [ { '$ifNull': [ '$$ck', None ] }, None ] }, { '$eq': [ { '$ifNull': [ '$$pk', None ] }, None ] } ] }, [], { '$concatArrays': [ { '$cond': [ { '$eq': [ { '$ifNull': [ '$$ck', None ] }, None ] }, [], [ { 'k': 'curr', 'v': { '$round': [ { '$ifNull': [ '$$ck', 0 ] }, 3 ] } } ] ] }, { '$cond': [ { '$eq': [ { '$ifNull': [ '$$pk', None ] }, None ] }, [], [ { 'k': 'pre', 'v': { '$round': [ { '$ifNull': [ '$$pk', 0 ] }, 3 ] } } ] ] }, { '$cond': [ { '$or': [ { '$eq': [ { '$ifNull': [ '$$ck', 0 ] }, 0 ] }, { '$eq': [ { '$ifNull': [ '$$pk', 0 ] }, 0 ] } ] }, [], [ { 'k': 'growth', 'v': { '$cond': [ { '$in': [ '$$this.value', '$percentkeys' ] }, { '$round': [ { '$subtract': [ '$$ck', '$$pk' ] }, 3 ] }, { '$round': [ { '$multiply': [ { '$subtract': [ { '$divide': [ '$$ck', '$$pk' ] }, 3 ] }, 100 ] }, 2 ] } ] } }, { 'k': 'growing', 'v': { '$gt': [ '$$ck', '$$pk' ] } } ] ] } ] } ] } } } }, 'in': { '$cond': [ { '$eq': [ { '$size': '$$data' }, 0 ] }, [], [ { 'k': '$$this.value', 'v': { '$arrayToObject': '$$data' } } ] ] } } }, [] ] } ] } } } } } }
        pipeline.extend([createCurrPreObjects, addCalculatedFields, addCurrPre, addGrowth])
        pipeline.extend([{ '$set': { 'uid': self.marketplace.uid, 'marketplace': self.marketplace.id, 'queryid': '$_id', '_id': { '$concat': [ { '$toString': '$marketplace' }, '_', { '$toString': '$_id' }, '_', '$collatetype', '_', { '$toString': '$value' } ] }, 'parent': { '$switch': { 'branches': [ { 'case': { '$eq': [ '$collatetype', 'sku' ] }, 'then': '$asin' }, { 'case': { '$eq': [ '$collatetype', 'asin' ] }, 'then': '$parentsku' }, { 'case': { '$eq': [ '$collatetype', 'parentsku' ] }, 'then': '$producttype' } ], 'default': None } } } }, { '$project': { 'data': 1, 'queryid': 1, 'value': 1, 'collatetype': 1, 'parent': 1 } }])
        pipeline.append(self.dbClient.queries.db.pp.merge(CollectionType.QUERY_RESULTS, 'replace', 'insert'))
        print(pipeline)
        await self.dbClient.queries.db.aggregate(pipeline)
        return await self.getNextQuery(query)