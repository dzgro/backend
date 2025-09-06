from datetime import datetime, timedelta
from bson import ObjectId
from dzgroshared.models.enums import CollectionType
from dzgroshared.models.collections.analytics import Month, MonthDataRequest, PeriodDataRequest, SingleMetricPeriodDataRequest
from dzgroshared.db.collections.pipelines import Get30DaysGraph, GetPeriodData, GetStateDataByMonth, GetMonthCarousel, GetListParams
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.extras import Analytics
from dzgroshared.models.extras import Analytics as AnalyticsModel

class DashboardHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.MARKETPLACES.value), uid=self.uid, marketplace=self.marketplace)

    async def getAllDates(self)->list[datetime]:
        matchDict = {"$match": {"_id": self.marketplace, "uid": self.uid}}
        setDates = self.db.pp.set({ 'dates': { '$reduce': { 'input': { '$range': [ 0, { '$sum': [ { '$dateDiff': { 'startDate': '$startDate', 'endDate': '$endDate', 'unit': 'day' } }, 1 ] }, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateSubtract': { 'startDate': '$endDate', 'unit': 'day', 'amount': '$$this' } } ] ] } } } })
        project = self.db.pp.project(['dates'],['_id'])
        result = await self.db.aggregate([matchDict, setDates, project])
        return result[0]['dates']
    
    async def getPerformanceParams(self):
        pipeline = GetListParams.execute(self.db.pp)
        data = await self.db.aggregate(pipeline)
        return data[0]
    
    async def getDates(self)->dict:
        matchDict = {"$match": {"_id": self.marketplace, "uid": self.uid}}
        project = self.db.pp.project(['startDate','endDate'],['_id'])
        result = await self.db.aggregate([matchDict, project])
        return result[0]

    async def getPeriodData(self, req: PeriodDataRequest):
        pipeline = GetPeriodData.pipeline(self.db.pp, req)
        data = await self.db.aggregate(pipeline)
        return Analytics.transformData('Period',data, req)
    
    async def getChartData(self, req: SingleMetricPeriodDataRequest):
        pipeline = Get30DaysGraph.pipeline(self.uid, self.marketplace, req)
        return await self.db.aggregate(pipeline)
    
    async def getMonthlyDataTable(self, req: PeriodDataRequest):
        # pipeline = GetMonthData.pipeline(self.db.pp, req.collatetype, req.value)
        # return await self.db.aggregate(pipeline)
        pass
    
    def getPipelineForDataBetweenTwoDates(self, req: PeriodDataRequest, startdate: datetime, enddate: datetime):
        letdict = { 'uid': '$uid', 'marketplace': '$marketplace', 'date': '$date', 'collatetype': 'marketplace' }
        if req.value: letdict['value'] = req.value
        matchDict ={ '$expr': { '$and': [ { '$eq': [ '$uid', self.uid ] }, { '$eq': [ '$marketplace', self.marketplace ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$gte': [ '$date', startdate ] }, { '$lte': [ '$date', enddate ] } ] } }
        if req.value: matchDict['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
        pipeline = [
            { '$match': { '_id': self.marketplace, 'uid': self.uid } },
            { '$set': { 'dates': { 'startdate': startdate, 'enddate': enddate } } }, 
            { '$lookup': { 'from': 'date_analytics', 'let': letdict, 'pipeline': [ { '$match': matchDict }, { '$project': { 'data': 1, '_id': 0 } } ], 'as': 'data' } }, 
            { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { 'date': '$date', 'data': { '$first': '$data.data' } } ] } } },
        ]
        missingkeys = Analytics.addMissingFields("data")
        derivedmetrics = Analytics.addDerivedMetrics("data")
        pipeline.append(missingkeys)
        pipeline.extend(derivedmetrics)
        return pipeline
    

    
    async def getMonthData(self, req: MonthDataRequest):
        month = next((Month.model_validate(x) for x in (await self.getMonths()) if x['month']==req.month), None)
        if not month: return ValueError("Invalid Month")
        pipeline = self.getPipelineForDataBetweenTwoDates(req, month.startdate, month.enddate)
        pipeline.append(AnalyticsModel.getProjectionStage('Month', req.collatetype))
        pipeline.append({"$project": {"data": 1}})
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.db.aggregate(pipeline)
        return Analytics.transformData('Month',data, req)
        
    
    async def getStateDataForMonths(self, req: PeriodDataRequest):
        # pipeline = GetMonthData.pipeline(self.db.pp, req.collatetype, req.value)
        # return await self.db.aggregate(pipeline)
        pass
    
    def getStateDataByMonth(self, req: PeriodDataRequest, month: str):
        pipeline = GetStateDataByMonth.pipeline(self.db.pp, req.collatetype, month, req.value)
        print(pipeline)
        return self.db.aggregate(pipeline)
        
    async def getMonths(self):
        def last_day_of_month(year: int, month: int) -> int:
            """Return the last day number (28–31) of the given month."""
            if month == 12:next_month = datetime(year + 1, 1, 1)
            else:next_month = datetime(year, month + 1, 1)
            return (next_month - timedelta(days=1)).day
        marketplace = await self.client.db.marketplaces.getMarketplace(self.marketplace)
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
        
        
    
    