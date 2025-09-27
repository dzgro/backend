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
    lookuppipeline = [matchStage, {"$replaceRoot": { "newRoot": "$data" }}]
    lookupdata = {
        '$lookup': {
            'from': CollectionType.DATE_ANALYTICS.value,
            'let': { 'marketplace': '$_id', 'startdate': '$months.startdate', 'enddate': '$months.enddate', "value": req.value, "collatetype": req.collatetype.value }, 
            'pipeline': lookuppipeline,
            'as': 'data'
        }
    }
    pipeline.extend([lookupdata, pp.collateData(), controller.addMissingFields()]+controller.addDerivedMetrics())
    pipeline.append({ "$replaceRoot": { "newRoot": { "$mergeObjects": [ "$months", { "data": "$data" } ] } } })
    return pipeline