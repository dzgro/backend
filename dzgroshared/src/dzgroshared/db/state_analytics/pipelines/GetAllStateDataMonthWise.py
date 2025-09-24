from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollectionType
from dzgroshared.analytics import controller
from dzgroshared.db.model import PeriodDataRequest

def pipeline(marketplace: ObjectId, req: PeriodDataRequest) -> list[dict]:
    pp = PipelineProcessor(None, marketplace)
    pipeline: list[dict] = pp.openMarketplaceMonths()
    lookuppipelineQueries = [ { '$eq': [ '$marketplace', '$$marketplace' ] }, {'$eq': ["$collatetype", "$$collatetype"]} ]
    if req.value is not None: lookuppipelineQueries.append( { '$eq': [ "$value", "$$value" ] } )
    lookuppipelineQueries.extend([ { '$gte': [ '$date', '$$startdate' ] }, { '$lte': [ '$date', '$$enddate' ] } ])
    matchStage = { '$match': { '$expr': { '$and': lookuppipelineQueries } } }
    lookuppipeline = [matchStage, {"$replaceWith":{ "state": "$data._id", "data": "$data.data" }}]
    lookupdata = {
        '$lookup': {
            'from': CollectionType.STATE_ANALYTICS.value,
            'let': { 'marketplace': '$_id', 'startdate': '$months.startdate', 'enddate': '$months.enddate', "value": req.value, "collatetype": req.collatetype.value }, 
            'pipeline': lookuppipeline,
            'as': 'state'
        }
    }
    pipeline.extend([lookupdata, pp.unwind("$state"), {"$replaceWith": pp.mergeObjects(["$state", "$months"])}])
    pipeline.extend([pp.collateData(), controller.addMissingFields()]+controller.addDerivedMetrics())
    groupByMonth = {
        "$group": {
            "_id": { "month": "$month", "period": "$period" },
            "data": { "$push": {
                "state": "$state",
                "data": "$data"
            } }
        }
    }
    replaceRoot = {
        "$replaceRoot": {
            "newRoot": pp.mergeObjects(["$_id", { "data": "$data" }])
        }
    }
    pipeline.extend([groupByMonth, replaceRoot])
    pipeline.append({"$sort": { "data.netrevenue": -1 }})
    return pipeline