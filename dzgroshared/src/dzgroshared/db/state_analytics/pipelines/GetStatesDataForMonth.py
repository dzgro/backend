from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollectionType
from dzgroshared.analytics import controller
from dzgroshared.db.model import MonthDataRequest, PeriodDataRequest

def pipeline(marketplace: ObjectId, req: MonthDataRequest) -> list[dict]:
    pp = PipelineProcessor(None, marketplace)
    pipeline: list[dict] = pp.openMarketplaceMonths()
    pipeline.append({"$match": {"months.month": req.month}})
    lookuppipelineQueries = [ { '$eq': [ '$marketplace', '$$marketplace' ] }, {'$eq': ["$collatetype", "$$collatetype"]} ]
    if req.value is not None: lookuppipelineQueries.append( { '$eq': [ "$value", "$$value" ] } )
    lookuppipelineQueries.extend([ { '$gte': [ '$date', '$$startdate' ] }, { '$lte': [ '$date', '$$enddate' ] } ])
    matchStage = { '$match': { '$expr': { '$and': lookuppipelineQueries } } }
    lookuppipeline = [matchStage, { "$replaceWith": { "state": "$state", "data": "$data" } }]
    lookupdata = {
        '$lookup': {
            'from': CollectionType.STATE_ANALYTICS.value,
            'let': { 'marketplace': '$_id', 'startdate': '$months.startdate', 'enddate': '$months.enddate', "value": req.value, "collatetype": req.collatetype.value }, 
            'pipeline': lookuppipeline,
            'as': 'state'
        }
    }
    pipeline.append(lookupdata)
    mergeStates = {"$set": {"state":{"$reduce":{"input":"$state","initialValue":[],"in":{"$let":{"vars":{"idx":{"$indexOfArray":["$$value.state","$$this.state"]}},"in":{"$cond":{"if":{"$eq":["$$idx",-1]},"then":{"$concatArrays":["$$value",[{"state":"$$this.state","data":["$$this.data"]}]]},"else":{"$map":{"input":"$$value","as":"v","in":{"$cond":{"if":{"$ne":["$$v.state","$$this.state"]},"then":"$$v","else":{"$mergeObjects":["$$v",{"data":{"$concatArrays":["$$v.data",["$$this.data"]]}}]}}}}}}}}}}}}}
    pipeline.extend([mergeStates, pp.unwind("$state"), {"$replaceWith": pp.mergeObjects(["$state", "$months"])}])
    pipeline.extend([pp.collateData(), controller.addMissingFields()]+controller.addDerivedMetrics())
    pipeline.append({"$sort": { "data.netrevenue": -1 }})
    return pipeline