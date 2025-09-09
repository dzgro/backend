from datetime import datetime, timedelta
from typing import Literal
from bson import ObjectId
from dzgroshared.models.enums import CollectionType
from dzgroshared.models.collections.analytics import Month, MonthDataRequest, PeriodDataRequest, SingleMetricPeriodDataRequest, StateDetailedDataByStateRequest
from dzgroshared.db.collections.pipelines import Get30DaysGraph, GetPeriodData, GetMonthCarousel, GetListParams
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.extras import Analytics
from dzgroshared.models.extras import Analytics as AnalyticsModel

class DashboardHelper:
    db: DbManager
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.MARKETPLACES.value), uid=self.client.uid)

    async def getAllDates(self)->list[datetime]:
        matchDict = {"$match": {"_id": self.client.marketplaceId}}
        setDates = self.db.pp.set({ 'dates': { '$reduce': { 'input': { '$range': [ 0, { '$sum': [ { '$dateDiff': { 'startDate': '$startDate', 'endDate': '$endDate', 'unit': 'day' } }, 1 ] }, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateSubtract': { 'startDate': '$endDate', 'unit': 'day', 'amount': '$$this' } } ] ] } } } })
        project = self.db.pp.project(['dates'],['_id'])
        result = await self.db.aggregate([matchDict, setDates, project])
        return result[0]['dates']
    
    async def getPerformanceParams(self):
        pipeline = GetListParams.execute(self.db.pp)
        data = await self.db.aggregate(pipeline)
        return data[0]
    
    async def getDates(self)->dict:
        matchDict = {"$match": {"_id": self.client.marketplaceId}}
        project = self.db.pp.project(['startDate','endDate'],['_id'])
        result = await self.db.aggregate([matchDict, project])
        return result[0]

    async def getPeriodData(self, req: PeriodDataRequest):
        pipeline = GetPeriodData.pipeline(self.db.pp, req)
        data = await self.db.aggregate(pipeline)
        return {"data": Analytics.transformData('Period',data, req.collatetype, self.client.marketplace.countrycode)}

    async def getChartData(self, req: SingleMetricPeriodDataRequest):
        pipeline = Get30DaysGraph.pipeline(self.client.marketplaceId, req)
        return await self.db.aggregate(pipeline)
    
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
        pipeline.append(Analytics.addMissingFields("data"))
        pipeline.extend(Analytics.addDerivedMetrics("data"))
        pipeline.append(Analytics.getProjectionStage('Month', req.collatetype))
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.db.aggregate(pipeline)
        months = [{"month": x['month'], "period": x['period']} for x in data]
        data = Analytics.transformData('Month',data, req.collatetype, self.client.marketplace.countrycode)
        return {"columns": months, "rows": data}
    
    async def getMonthDatesDataTable(self, req: MonthDataRequest):
        month = next((Month.model_validate(x) for x in (await self.getMonths()) if x['month']==req.month), None)
        if not month: return ValueError("Invalid Month")
        matchdict = { 'marketplace': self.client.marketplaceId, 'collatetype': req.collatetype, 'date': {'$gte': month.startdate, '$lte': month.enddate} }
        if req.value: matchdict['value'] = req.value
        pipeline = [
            { '$match': matchdict},
            { '$sort': { 'date':1} },
            { '$set': { 'date':{'$dateToString': { 'format': '%d-%b', 'date': '$date' }}} },
            { '$project': { 'date':1,'data':1, '_id':0} },
        ]
        missingkeys = Analytics.addMissingFields("data")
        derivedmetrics = Analytics.addDerivedMetrics("data")
        pipeline.append(missingkeys)
        pipeline.extend(derivedmetrics)
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.client.db.date_analytics.db.aggregate(pipeline)
        dates = [x['date'] for x in data]
        data = Analytics.transformData('Month Date',data, req.collatetype, self.client.marketplace.countrycode)
        columns = Analytics.convertSchematoMultiLevelColumns('Month Date')
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
        missingkeys = Analytics.addMissingFields("data")
        derivedmetrics = Analytics.addDerivedMetrics("data")
        pipeline.append(missingkeys)
        pipeline.extend(derivedmetrics)
        return pipeline
    
    
    async def getMonthLiteData(self, req: MonthDataRequest):
        month = next((Month.model_validate(x) for x in (await self.getMonths()) if x['month']==req.month), None)
        if not month: return ValueError("Invalid Month")
        pipeline = self.getPipelineForDataBetweenTwoDates(req, month.startdate, month.enddate)
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.db.aggregate(pipeline)
        monthMeterGroups = Analytics.transformData('Month Meters',data, req.collatetype, self.client.marketplace.countrycode)
        monthBars = Analytics.transformData('Month Bars',data, req.collatetype, self.client.marketplace.countrycode)
        monthdata = Analytics.transformData('Month Data',data, req.collatetype, self.client.marketplace.countrycode)
        return {
            "month": req.month,
            "meterGroups": monthMeterGroups[0]['data'] if len(monthMeterGroups)>0 and 'data' in monthMeterGroups[0] else [],
            "bars": monthBars[0]['data'][0] if len(monthBars)>0 and 'data' in monthBars[0] and len(monthBars[0]['data'])>0 else [],
            "data": monthdata[0]['data'][0] if len(monthdata)>0 and 'data' in monthdata[0] and len(monthdata[0]['data'])>0 else [],
        }
    
    async def getStateWiseData(self, req: MonthDataRequest, schemaType: Analytics.SchemaType):
        month = next((Month.model_validate(x) for x in (await self.getMonths()) if x['month']==req.month), None)
        if not month: raise ValueError("Invalid Month")
        letdict = { 'marketplace': '$marketplace', 'date': '$date', 'collatetype': 'marketplace' }
        if req.value: letdict['value'] = req.value
        matchDict ={ '$expr': { '$and': [ { '$eq': [ '$marketplace', self.client.marketplaceId ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$gte': [ '$date', month.startdate ] }, { '$lte': [ '$date', month.enddate ] } ] } }
        if req.value: matchDict['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
        pipeline = [
            { '$match': { '_id': self.client.marketplaceId} },
            { '$set': { 'dates': { 'startdate': month.startdate, 'enddate': month.enddate } } }, 
            { '$lookup': { 'from': CollectionType.STATE_ANALYTICS.value, 'let': letdict, 'pipeline': [ { '$match': matchDict }, { "$group": { "_id": "$state", "data": { "$push": "$data" } } } ], 'as': 'data' } }, 
            {"$unwind":"$data"},
            {"$replaceWith":{ "state": "$data._id", "data": "$data.data" }},
            self.db.pp.collateData()
        ]
        missingkeys = Analytics.addMissingFields("data")
        derivedmetrics = Analytics.addDerivedMetrics("data")
        pipeline.append(missingkeys)
        pipeline.extend(derivedmetrics)
        pipeline.append(Analytics.getProjectionStage(schemaType, req.collatetype))
        pipeline.append({"$sort": { "data.netrevenue": -1 }})
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.db.aggregate(pipeline)
        return Analytics.transformData(schemaType,data, req.collatetype, self.client.marketplace.countrycode)

        
    
    async def getStateDataDetailedForMonth(self, req: MonthDataRequest):
        rows = await self.getStateWiseData(req, 'State All')
        columns = Analytics.convertSchematoMultiLevelColumns('State All')
        return {"columns": columns, "rows": rows}

    async def getStateDataLiteByMonth(self, req: MonthDataRequest):
        data = await self.getStateWiseData(req, 'State Lite')
        return {"data": [{"state": item['state'], 'data': item['data'][0]['items'] if len(item['data']) > 0 and 'items' in item['data'][0] else []} for item in data]}
    
    async def getStateDataDetailed(self, req: StateDetailedDataByStateRequest):
        letdict = { 'marketplace': '$marketplace', 'startdate': '$startdate', 'enddate': '$enddate', 'collatetype': 'marketplace', 'state': req.state }
        if req.value: letdict['value'] = req.value
        matchDict ={ '$expr': { '$and': [ { '$eq': [ '$marketplace', self.client.marketplaceId ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$gte': [ '$date', '$$startdate' ] }, { '$lte': [ '$date', '$$enddate' ] }, { '$eq': [ '$state', '$$state' ] } ] } }
        if req.value: matchDict['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
        pipeline = [
            { '$match': { '_id': self.client.marketplaceId } },
            { '$set': { 'month': { '$let': { 'vars': { 'start': { '$dateTrunc': { 'date': '$dates.startdate', 'unit': 'month' } }, 'end': { '$dateTrunc': { 'date': '$dates.enddate', 'unit': 'month' } } }, 'in': { '$map': { 'input': { '$range': [ 0, { '$add': [ { '$dateDiff': { 'startDate': '$$start', 'endDate': '$$end', 'unit': 'month' } }, 1 ] } ] }, 'as': 'i', 'in': { '$let': { 'vars': { 'curMonthStart': { '$dateAdd': { 'startDate': '$$start', 'unit': 'month', 'amount': '$$i' } }, 'nextMonthStart': { '$dateAdd': { 'startDate': '$$start', 'unit': 'month', 'amount': { '$add': [ '$$i', 1 ] } } } }, 'in': { '$let': { 'vars': { 'month': { '$dateToString': { 'date': '$$curMonthStart', 'format': '%b %Y' } }, 'startdate': { '$cond': [ { '$eq': [ '$$i', 0 ] }, '$dates.startdate', '$$curMonthStart' ] }, 'enddate': { '$cond': [ { '$eq': [ '$$nextMonthStart', { '$dateAdd': { 'startDate': '$$end', 'unit': 'month', 'amount': 1 } } ] }, '$dates.enddate', { '$dateAdd': { 'startDate': '$$nextMonthStart', 'unit': 'day', 'amount': -1 } } ] } }, 'in': { 'month': '$$month', 'startdate': '$$startdate', 'enddate': '$$enddate', 'period': { '$concat': [ { '$dateToString': { 'date': '$$startdate', 'format': '%d %b' } }, ' - ', { '$dateToString': { 'date': '$$enddate', 'format': '%d %b' } } ] } } } } } } } } } } }},
            { '$unwind': { 'path': '$month' } }, 
            { '$replaceWith': '$month' }, 
            { '$lookup': { 'from': 'state_analytics', 'let': letdict, 'pipeline': [ { '$match': matchDict }, { '$group': { '_id': '$state', 'data': { '$push': '$data' } } } ], 'as': 'data' } }, 
            { '$unwind': { 'path': '$data' } }, 
            { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { 'data': '$data.data' } ] } } },
            self.db.pp.collateData(),
            {"$sort": { "startdate": -1 }},
            {"$replaceRoot": { "newRoot": { "month": "$month", "period": "$period", "data": "$data" } }}
        ]
        pipeline.append(Analytics.addMissingFields("data"))
        pipeline.extend(Analytics.addDerivedMetrics("data"))
        pipeline.append(Analytics.getProjectionStage('State Detail', req.collatetype))
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.db.aggregate(pipeline)
        months = [{"month": x['month'], "period": x['period']} for x in data]
        data = Analytics.transformData('State Detail',data, req.collatetype, self.client.marketplace.countrycode)
        return {"columns": months, "rows": data}
        
    
    # async def getAllStateWithMonths(self, req: MonthDataRequest):
    #     month = next((Month.model_validate(x) for x in (await self.getMonths()) if x['month']==req.month), None)
    #     if not month: return ValueError("Invalid Month")
    #     pipeline = self.getPipelineForStateDataBetweenTwoDates(req, month.startdate, month.enddate)
    #     pipeline.append(Analytics.getProjectionStage('State Lite', req.collatetype))
    #     pipeline.append(Analytics.getProjectionStage('State Lite', req.collatetype))
    #     from dzgroshared.utils import mongo_pipeline_print
    #     mongo_pipeline_print.copy_pipeline(pipeline)
    #     data = await self.db.aggregate(pipeline)
    #     data = Analytics.transformData('State Lite',data, req)
    #     return {"data": [{"state": item['state'], 'data': item['data'][0]['items'] if len(item['data']) > 0 and 'items' in item['data'][0] else []} for item in data]}

    async def getMonths(self):
        def last_day_of_month(year: int, month: int) -> int:
            """Return the last day number (28–31) of the given month."""
            if month == 12:next_month = datetime(year + 1, 1, 1)
            else:next_month = datetime(year, month + 1, 1)
            return (next_month - timedelta(days=1)).day
        marketplace = await self.client.db.marketplaces.getMarketplace(self.client.marketplaceId)
        year, month = marketplace.dates.startdate.year, marketplace.dates.startdate.month
        end_year, end_month = marketplace.dates.enddate.year, marketplace.dates.enddate.month
        results = []
        while (year, month) <= (end_year, end_month):
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, last_day_of_month(year, month))
            range_start = max(first_day, marketplace.dates.startdate)
            range_end = min(last_day, marketplace.dates.enddate)
            results.append({
                "month": first_day.strftime("%b %Y"),
                "period": f"{range_start.strftime('%d %b')} - {range_end.strftime('%d %b')}",
                "startdate": range_start,
                "enddate": range_end
            })
            month += 1
            if month > 12:
                month = 1
                year += 1
        return results
        
        
    
    