from datetime import datetime
from bson import ObjectId
from dzgroshared.analytics import controller
from dzgroshared.db.date_analytics.pipelines import Get30DaysGraph
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.model import Month, MonthDataRequest, PeriodDataRequest, SingleMetricPeriodDataRequest

class DateAnalyticsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.DATE_ANALYTICS.value), marketplace=client.marketplaceId)
    
    
    async def getMonthlyDataTable(self, req: PeriodDataRequest):
        letdict = {'marketplace': '$marketplace', 'startdate': '$startdate', 'enddate': '$enddate', 'collatetype': 'marketplace' }
        if req.value: letdict['value'] = req.value
        matchDict ={ '$expr': { '$and': [ { '$eq': [ '$marketplace', self.client.marketplaceId ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$gte': [ '$date', '$$startdate' ] }, { '$lte': [ '$date', '$$enddate' ] }] } }
        if req.value: matchDict['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
        pipeline = [
            { '$match': { '_id': self.client.marketplaceId} },
            { '$set': { 'month': { '$let': { 'vars': { 'start': { '$dateTrunc': { 'date': '$dates.startdate', 'unit': 'month' } }, 'end': { '$dateTrunc': { 'date': '$dates.enddate', 'unit': 'month' } } }, 'in': { '$map': { 'input': { '$range': [ 0, { '$add': [ { '$dateDiff': { 'startDate': '$$start', 'endDate': '$$end', 'unit': 'month' } }, 1 ] } ] }, 'as': 'i', 'in': { '$let': { 'vars': { 'curMonthStart': { '$dateAdd': { 'startDate': '$$start', 'unit': 'month', 'amount': '$$i' } }, 'nextMonthStart': { '$dateAdd': { 'startDate': '$$start', 'unit': 'month', 'amount': { '$add': [ '$$i', 1 ] } } } }, 'in': { '$let': { 'vars': { 'month': { '$dateToString': { 'date': '$$curMonthStart', 'format': '%b %Y' } }, 'startdate': { '$cond': [ { '$eq': [ '$$i', 0 ] }, '$dates.startdate', '$$curMonthStart' ] }, 'enddate': { '$cond': [ { '$eq': [ '$$nextMonthStart', { '$dateAdd': { 'startDate': '$$end', 'unit': 'month', 'amount': 1 } } ] }, '$dates.enddate', { '$dateAdd': { 'startDate': '$$nextMonthStart', 'unit': 'day', 'amount': -1 } } ] } }, 'in': { 'month': '$$month', 'startdate': '$$startdate', 'enddate': '$$enddate', 'period': { '$concat': [ { '$dateToString': { 'date': '$$startdate', 'format': '%d %b' } }, ' - ', { '$dateToString': { 'date': '$$enddate', 'format': '%d %b' } } ] } } } } } } } } } } }},
            { '$unwind': { 'path': '$month' } }, 
            { '$replaceWith': '$month' }, 
            { '$lookup': { 'from': 'date_analytics', 'let': letdict, 'pipeline': [ { '$match': matchDict },{"$replaceWith": "$data"}], 'as': 'data' } }, 
            self.db.pp.collateData(),
            {"$sort": { "startdate": -1 }},
            {"$replaceRoot": { "newRoot": { "month": "$month", "period": "$period", "data": "$data" } }}
        ]
        pipeline.append(controller.addMissingFields("data"))
        pipeline.extend(controller.addDerivedMetrics("data"))
        pipeline.append(controller.getProjectionStage('Month', req.collatetype))
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        months = [{"month": x['month'], "period": x['period']} for x in data]
        data = controller.transformData('Month',data, req.collatetype, self.client.marketplace.countrycode)
        return {"columns": months, "rows": data}
    
    async def getMonthDatesDataTable(self, req: MonthDataRequest):
        month = next((Month.model_validate(x) for x in (await self.client.db.marketplaces.getMonths()) if x['month']==req.month), None)
        if not month: return ValueError("Invalid Month")
        matchdict = { 'marketplace': self.client.marketplaceId, 'collatetype': req.collatetype, 'date': {'$gte': month.startdate, '$lte': month.enddate} }
        if req.value: matchdict['value'] = req.value
        pipeline = [
            { '$match': matchdict},
            { '$sort': { 'date':1} },
            { '$set': { 'date':{'$dateToString': { 'format': '%d-%b', 'date': '$date' }}} },
            { '$project': { 'date':1,'data':1, '_id':0} },
        ]
        missingkeys = controller.addMissingFields("data")
        derivedmetrics = controller.addDerivedMetrics("data")
        pipeline.append(missingkeys)
        pipeline.extend(derivedmetrics)
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.client.db.date_analytics.db.aggregate(pipeline)
        if not data: raise ValueError("No Data Found")
        dates = [x['date'] for x in data]
        data = controller.transformData('Month Date',data, req.collatetype, self.client.marketplace.countrycode)
        columns = controller.convertSchematoMultiLevelColumns('Month Date')
        return {"columns": columns, "rows": data}

    def getPipelineForDataBetweenTwoDates(self, req: PeriodDataRequest, startdate: datetime, enddate: datetime):
        letdict = { 'marketplace': '$marketplace', 'date': '$date', 'collatetype': 'marketplace' }
        if req.value: letdict['value'] = req.value
        matchDict ={ '$expr': { '$and': [{ '$eq': [ '$marketplace', self.client.marketplaceId ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$gte': [ '$date', startdate ] }, { '$lte': [ '$date', enddate ] } ] } }
        if req.value: matchDict['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
        pipeline = [
            { '$match': { '_id': self.client.marketplaceId,} },
            { '$set': { 'dates': { 'startdate': startdate, 'enddate': enddate } } }, 
            { '$lookup': { 'from': CollectionType.DATE_ANALYTICS.value, 'let': letdict, 'pipeline': [ { '$match': matchDict }, { "$replaceRoot": { "newRoot": "$data" } } ], 'as': 'data' } }, 
            self.db.pp.collateData(),
            { '$project': { 'data':1, "_id": 0 } },
        ]
        missingkeys = controller.addMissingFields("data")
        derivedmetrics = controller.addDerivedMetrics("data")
        pipeline.append(missingkeys)
        pipeline.extend(derivedmetrics)
        return pipeline
    
    
    async def getMonthLiteData(self, req: PeriodDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_complete_month_lite_data_pipeline(req)
        result = await self.client.db.marketplaces.db.aggregate(pipeline)
        return {"data": result}
    
    async def getPeriodData(self, req: PeriodDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_period_pipeline(req)
        result = await self.client.db.marketplaces.db.aggregate(pipeline)
        return {"data": result}