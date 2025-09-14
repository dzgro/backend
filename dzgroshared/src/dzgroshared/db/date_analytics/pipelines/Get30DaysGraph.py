
from bson import ObjectId
from dzgroshared.analytics import controller
from dzgroshared.db.model import SingleMetricPeriodDataRequest


def pipeline(marketplace: ObjectId, req: SingleMetricPeriodDataRequest):
    letdict = {'marketplace': '$marketplace', 'date': '$date', 'collatetype': 'marketplace' }
    if req.value: letdict['value'] = req.value
    matchDict ={ '$expr': { '$and': [ { '$eq': [ '$marketplace', marketplace ] }, { '$eq': [ '$collatetype', '$$collatetype' ] }, { '$eq': [ '$date', '$$date' ] } ] } }
    if req.value: matchDict['$expr']['$and'].append({ '$eq': [ '$value', '$$value' ] })
    pipeline = [
        { '$match': { '_id': marketplace} }, 
        { '$set': { 'date': { '$reduce': { 'input': { '$range': [ 0, 30, 1 ] }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$dateSubtract': { 'startDate': '$dates.enddate', 'amount': '$$this', 'unit': 'day' } } ] ] } } } } }, 
        { '$unwind': { 'path': '$date' } },
        { '$lookup': { 'from': 'date_analytics', 'let': letdict, 'pipeline': [ { '$match': matchDict }, { '$project': { 'data': 1, '_id': 0 } } ], 'as': 'data' } }, 
        { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { 'date': '$date', 'data': { '$first': '$data.data' } } ] } } },
    ]
    missingkeys = controller.addMissingFields("data")
    derivedmetrics = controller.addDerivedMetrics("data")
    pipeline.append(missingkeys)
    pipeline.extend(derivedmetrics)
    key = f'data.{req.key.value}'
    pipeline.extend(
        [
            {"$project": {"date": 1, key:1}},
            { '$sort': { 'date': 1 } },
            { '$replaceRoot': { 'newRoot': { 'date': { '$dateToString': { 'date': '$date', 'format': '%b %d, %Y' } }, 'value': { '$round': [ { '$ifNull': [ f'${key}', 0 ] }, 1 ] } } } },
            { '$group': { '_id': None, 'dates': { '$push': '$date' }, 'values': { '$push': '$value' } } },
            { '$project': { '_id': 0 } }
        ]
    )
    from dzgroshared.utils import mongo_pipeline_print
    mongo_pipeline_print.copy_pipeline(pipeline)
    return pipeline