from bson import ObjectId
from dzgroshared.analytics import controller
from dzgroshared.db.state_analytics.model import StateDetailedDataByStateRequest
from dzgroshared.db.model import Month, MonthDataRequest
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.DbUtils import DbManager

class StateAnalyticsHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.STATE_ANALYTICS.value), marketplace=client.marketplaceId)

    async def getStateWiseData(self, req: MonthDataRequest, schemaType: controller.SchemaType):
        month = next((Month.model_validate(x) for x in (await self.client.db.marketplaces.getMonths()) if x['month']==req.month), None)
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
        missingkeys = controller.addMissingFields("data")
        derivedmetrics = controller.addDerivedMetrics("data")
        pipeline.append(missingkeys)
        pipeline.extend(derivedmetrics)
        pipeline.append(controller.getProjectionStage(schemaType, req.collatetype))
        pipeline.append({"$sort": { "data.netrevenue": -1 }})
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.db.aggregate(pipeline)
        return controller.transformData(schemaType,data, req.collatetype, self.client.marketplace.countrycode)

        
    
    async def getStateDataDetailedForMonth(self, req: MonthDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_state_all_pipeline(req)
        rows = await self.client.db.marketplaces.db.aggregate(pipeline)
        columns = controller.convertSchematoMultiLevelColumns('State All')
        return {"columns": columns, "rows": rows}

    async def getStateDataLiteByMonth(self, req: MonthDataRequest):
        from dzgroshared.analytics.AnalyticsPipelineBuilder import AnalyticsPipelineBuilder
        builder = AnalyticsPipelineBuilder(self.client.marketplaceId, self.client.marketplace.countrycode)
        pipeline = builder.get_state_lite_pipeline(req)
        data = await self.client.db.marketplaces.db.aggregate(pipeline)
        return {"data": data}
    
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
        pipeline.append(controller.addMissingFields("data"))
        pipeline.extend(controller.addDerivedMetrics("data"))
        pipeline.append(controller.getProjectionStage('State Detail', req.collatetype))
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        data = await self.db.aggregate(pipeline)
        months = [{"month": x['month'], "period": x['period']} for x in data]
        data = controller.transformData('State Detail',data, req.collatetype, self.client.marketplace.countrycode)
        return {"columns": months, "rows": data}
