from bson import ObjectId
from dzgroshared.db.enums import CollateType, CollectionType


def pipeline(marketplace: ObjectId, queryid: ObjectId|None = None) -> list[dict]:
    pipeline: list[dict] = [{"$match": {"marketplace": marketplace}}]
    if queryid: pipeline.append({"$match": {"_id": queryid}})
    pipeline.extend([{"$set": {"collatetype": CollateType.list()}}, {"$unwind": "$collatetype"}])
    pipeline.append({ "$addFields": { "currdates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$curr.startdate", "endDate": "$curr.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$curr.startdate", "unit": "day", "amount": "$$i" } } } }, "predates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$pre.startdate", "endDate": "$pre.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$pre.startdate", "unit": "day", "amount": "$$i" } } } } } } )
    pipeline.append({ '$lookup': { 'from': 'date_analytics', 'let': { 'currdates': '$currdates','predates': '$predates', 'collatetype': "$collatetype", 'dates': {"$setUnion": {"$concatArrays": ["$currdates","$predates"]}} }, 'pipeline': [ { '$match': { '$expr': { '$and': [ {"$eq": ["$marketplace", marketplace]},{"$eq": ["$collatetype", "$$collatetype"]},{ '$in': [ '$date', '$$dates' ] } ] } } }, { '$group': { '_id': {'value': '$value', "parentsku": "$parentsku","category": "$category",}, 'data': { '$push': '$$ROOT' } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', 
{
              "$cond": {
                "if": {
                  "$eq": [
                    {"$ifNull": ["$_id.parentsku", False]},
                    False
                  ]
                },
                "then": {},
                "else": {"parentsku": "$_id.parentsku"}
              }
            },
            {
              "$cond": {
                "if": {
                  "$eq": [
                    {"$ifNull": ["$_id.category", False]},
                    False
                  ]
                },
                "then": {},
                "else": {"category": "$_id.category"}
              }
            }, { '$reduce': { 'input': '$data', 'initialValue': { 'curr': [], 'pre': [] }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$in': [ '$$this.date', "$$currdates" ] }, 'then': { 'curr': { '$concatArrays': [ '$$value.curr', [ '$$this.data' ] ] } }, 'else': { '$cond': { 'if': { '$in': [ '$$this.date', "$$predates" ] }, 'then': { 'pre': { '$concatArrays': [ '$$value.pre', [ '$$this.data' ] ] } }, 'else': {} } } } } ] } } } ] } } }, { '$set': { 'curr': { '$reduce': { 'input': '$curr', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } }, 'pre': { '$reduce': { 'input': '$pre', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } } } } ], 'as': 'data' } })
    pipeline.extend([{ '$unwind': { 'path': '$data', 'preserveNullAndEmptyArrays': False } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$data', { 'queryid': '$_id', "collatetype": "$collatetype" } ] } } }])
    from dzgroshared.analytics import controller
    pipeline.append(controller.addMissingFields('curr'))
    pipeline.extend(controller.addDerivedMetrics('curr'))
    pipeline.append(controller.addMissingFields('pre'))
    pipeline.extend(controller.addDerivedMetrics('pre'))
    pipeline.append(controller.addGrowth())
    pipeline.append(controller.create_comparison_data())
    pipeline.append(controller.getProjectionStage('Comparison Table', CollateType.MARKETPLACE))
    pipeline.extend([{"$set": {"marketplace": marketplace}}, {"$project": {"curr": 0, "pre": 0,'growth':0}}, {"$merge": CollectionType.PERFORMANCE_PERIOD_RESULTS.value}])
    return pipeline