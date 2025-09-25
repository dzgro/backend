from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollectionType
from dzgroshared.analytics import controller
from dzgroshared.db.state_analytics.model import StateRequest

def pipeline(marketplace: ObjectId, req: StateRequest) -> list[dict]:
    pp = PipelineProcessor(None, marketplace)
    pipeline: list[dict] = pp.openMarketplaceMonths()
    lookuppipelineQueries = [ { '$eq': [ '$marketplace', '$$marketplace' ] }, {'$eq': ["$collatetype", "$$collatetype"]} ]
    if req.value is not None: lookuppipelineQueries.append( { '$eq': [ "$value", "$$value" ] } )
    lookuppipelineQueries.extend([ { '$gte': [ '$date', '$$startdate' ] }, { '$lte': [ '$date', '$$enddate' ] }, { '$eq': [ '$state', '$$state' ] } ])
    matchStage = { '$match': { '$expr': { '$and': lookuppipelineQueries } } }
    lookuppipeline = [matchStage, {"$replaceWith":"$data"}]
    lookupdata = {
        '$lookup': {
            'from': CollectionType.STATE_ANALYTICS.value,
            'let': { 'marketplace': '$_id', 'startdate': '$months.startdate', 'enddate': '$months.enddate', "value": req.value, "collatetype": req.collatetype.value, 'state': req.state }, 
            'pipeline': lookuppipeline,
            'as': 'state'
        }
    }
    pipeline.extend([lookupdata, {"$replaceWith": pp.mergeObjects([{"data": "$data"}, "$months"])}])
    pipeline.extend([pp.collateData(), controller.addMissingFields()]+controller.addDerivedMetrics())
    return pipeline