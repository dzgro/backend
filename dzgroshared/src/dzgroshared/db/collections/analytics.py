from datetime import datetime
from bson import ObjectId
from dzgroshared.models.enums import CollateType,CollectionType
from dzgroshared.models.collections.analytics import CollateTypeAndValue
from dzgroshared.db.collections.pipelines import Get30DaysGraph, GetPeriodData, GetMonthData, GetStateDataByMonth, GetMonthCarousel, GetListParams
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class DashboardHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.marketplace = marketplace
        self.uid = uid
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

    async def getPeriodData(self, req: CollateTypeAndValue):
        pipeline = GetPeriodData.pipeline(self.db.pp, req)
        data = await self.db.aggregate(pipeline)
        if req.collatetype!=CollateType.MARKETPLACE: data.pop()
        return data
    
    async def getChartData(self, key:str, req: CollateTypeAndValue):
        pipeline = Get30DaysGraph.pipeline(self.db.pp, req.collatetype, key, req.value)
        return await self.db.aggregate(pipeline)
    
    async def getMonthlyDataTable(self, req: CollateTypeAndValue):
        pipeline = GetMonthData.pipeline(self.db.pp, req.collatetype, req.value)
        return await self.db.aggregate(pipeline)
    
    async def getMonthlyCarousel(self, req: CollateTypeAndValue,month:str):
        pipeline = GetMonthCarousel.pipeline(self.db.pp, req.collatetype, month, req.value)
        data = await self.db.aggregate(pipeline)
        if len(data)>0: return data[0] 
        raise ValueError("Data not Available")
    
    async def getStateDataForMonths(self, req: CollateTypeAndValue):
        pipeline = GetMonthData.pipeline(self.db.pp, req.collatetype, req.value)
        return await self.db.aggregate(pipeline)
    
    def getStateDataByMonth(self, req: CollateTypeAndValue, month: str):
        pipeline = GetStateDataByMonth.pipeline(self.db.pp, req.collatetype, month, req.value)
        print(pipeline)
        return self.db.aggregate(pipeline)
        
    def getMonths(self):
        pipeline = [self.db.pp.match({"_id": self.db.pp.marketplace, "uid": self.db.pp.uid})]
        pipeline.extend(self.db.pp.getMonths())
        pipeline.append(self.db.pp.project([],["date","uid","marketplace"]))
        return self.db.aggregate(pipeline)

        
    
    