from typing import Literal
from bson import ObjectId
from dzgroshared.models.collections.analytics import ComparisonPeriodDataRequest, PeriodDataRequest
from dzgroshared.models.enums import AnalyticsMetric, AnalyticsMetricOperation, CollateType, CollectionType, CountryCode
from dzgroshared.models.model import StartEndDate
from dzgroshared.models.extras import Analytics


def transformData(schemaType: Analytics.SchemaType, data: list[dict], req: PeriodDataRequest):
    schema = Analytics.getSchema(schemaType, req.collatetype)
    return [{**d, "data": [transformPeriodData(s, d['data'], req.countrycode, 1) for s in schema]} for d in data]


percent_fields = [d.metric.value for d in Analytics.MetricDetails if d.ispercentage]
non_percent_fields = [d.metric.value for d in Analytics.MetricDetails if not d.ispercentage]

def addMissingFields(data_key: str = "data"):
    return { "$addFields": {f"{data_key}.{key.value}": {"$round": [{ "$ifNull": [f"${data_key}.{key.value}", 0] },2]} for key in AnalyticsMetric.values()} }

def format_number(value: float|None, metric: AnalyticsMetric, countrycode: CountryCode, isGrowth: bool=False) -> str|None:
    try:
        if value is None: return None
        if isGrowth:
            if metric.value in percent_fields: return f"{value:.1f}" if value>1 else f"{value:.2f}"
            return f"{value:.1f}%" if value>1 else f"{value:.2f}%"
        else:
            if metric.value in percent_fields: return f"{value:.2f}%"
            if metric.value in non_percent_fields:
                abs_val = abs(value)
                if abs_val >= 1e3 and abs_val < 1e5: return f"{abs_val/1e3:.2f} K"
                if countrycode==CountryCode.INDIA:
                    if abs_val >= 1e7: return f"{abs_val/1e7:.2f} Cr"
                    elif abs_val >= 1e5: return f"{abs_val/1e5:.2f} Lacs"
                else:
                    # International system: M / B
                    if abs_val >= 1e9: return f"{abs_val/1e9:.2f} B"
                    elif abs_val >= 1e6: return f"{abs_val/1e6:.2f} M"
                return f"{abs_val:.1f}" if isinstance(value, float) else f"{abs_val:.0f}"
            return f"{value:.2f}"
    except Exception as e:
        print(e)


def transformPeriodData(schema: dict, data: dict, countrycode: CountryCode, level=1):
    result: dict = {"label": schema['metric']}
    if level > 1 and "metric" in schema:
        key = AnalyticsMetric(schema['metric'])
        value = data.get(key.value, None)
        detail = next((d for d in Analytics.MetricDetails if d.metric == key), None)
        if detail:
            result['label'] = detail.label
            result['description'] = detail.description
        else: 
            result['label'] = schema['metric']
        result["value"] = value
        result["valueString"] = format_number(value, key, countrycode)
    if schema.get("items"):
        result["items"] = [
            transformPeriodData(item, data, countrycode, level + 1)
            for item in schema["items"]
        ]
    return result

def transformComparisonData(schema: dict, data: dict, countrycode: CountryCode, level=1):
    try:
        result: dict = {"label": schema['metric']}
        if level > 1 and "metric" in schema:
            key = AnalyticsMetric(schema['metric'])
            value = data.get(key.value, {})
            detail = next((d for d in Analytics.MetricDetails if d.metric == key), None)
            if detail:
                result['label'] = detail.label
                result['description'] = detail.description
                for k,v in value.items():
                    result[k] = {
                        "value": v,
                        "valueString": format_number(v, key, countrycode, k=='growth'),
                    }
                result['value'] =  f'{result['curr']['value']} vs {result['pre']['value']}'
                result['valueString'] =  f'{result['curr']['valueString']} vs {result['pre']['valueString']}'
                result['growing'] =  result['growth']['value']>0 if not detail.isReverseGrowth else result['growth']['value']<0
                result['growth'] =  result['growth']['valueString']
                del result['curr']
                del result['pre']
        if schema.get("items"):
            result["items"] = []
            for item in schema["items"]:
                x = transformComparisonData(item, data, countrycode, level + 1)
                result["items"].append(x)
        return result
    except Exception as e:
        print(e)

def transformCurrPreData(data: list[dict], countrycode: CountryCode):
    for item in data:
        for k,v in item['data'].items():
            key = AnalyticsMetric(k)
            newData = {}
            for k1,v1 in v.items():
                newData[k1] = format_number(v1, key, countrycode, k1=='growth')
        del item['data']
        item.update(newData)
    return data

def addDerivedMetrics(data_key: str = "data"):
    level1: dict = {}
    level2: dict = {}
    level3: dict = {}
    level4: dict = {}
    level5: dict = {}
    dk = f"${data_key}."
    for item in Analytics.METRIC_CALCULATIONS:
        result: dict = {}
        if item.operation == AnalyticsMetricOperation.SUM:
            result = { "$sum": [f"{dk}{m.value}" for m in item.metrics] }
        elif item.operation == AnalyticsMetricOperation.SUBTRACT:
            result = { "$subtract": [f"{dk}{m.value}" for m in item.metrics] }
        elif item.operation == AnalyticsMetricOperation.DIVIDE:
            multiplier = 100 if not item.avoidMultiplier else 1
            result = { "$cond": [ {"$gt": [f"{dk}{item.metrics[1].value}", 0]}, {"$round": [ {"$multiply": [ {"$divide": [f"{dk}{item.metrics[0].value}", f"{dk}{item.metrics[1].value}"]}, multiplier ]}, 2 ]}, 0 ] }
        elif item.operation == AnalyticsMetricOperation.MULTIPLY:
            result = { "$multiply": [f"{dk}{m.value}" for m in item.metrics] }
        if item.level == 0:
            level1.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 1:
            level2.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 2:
            level3.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 3:
            level4.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 4:
            level5.update( {f"{data_key}.{item.metric.value}": result} )
    return [{ "$addFields": level1 }, { "$addFields": level2 }, { "$addFields": level3 }, { "$addFields": level4 }, { "$addFields": level5 }]

def addGrowth():
    return { "$addFields": { "growth": { "$arrayToObject": { "$map": { "input": { "$objectToArray": "$curr" }, "as": "kv", "in": { "k": "$$kv.k", "v": { "$let": { "vars": { "currVal": "$$kv.v", "preVal": { "$getField": { "field": "$$kv.k", "input": "$pre" } }, "percentFields": percent_fields }, "in": { "$cond": [ { "$in": ["$$kv.k", "$$percentFields"] }, { "$cond": [ { "$lt": [{ "$abs": { "$subtract": ["$$currVal", "$$preVal"] } }, 10] }, { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 2] }, { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 1] } ] }, { "$cond": [ { "$or": [{ "$eq": ["$$preVal", 0] }, { "$eq": ["$$preVal", None] }] }, 0, { "$cond": [ { "$lt": [ { "$abs": { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] } }, 10 ] }, { "$round": [ { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] }, 2 ] }, { "$round": [ { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] }, 1 ] } ] } ] } ] } } } } } } } } }

def create_comparison_data():
    return { "$addFields": { "data": { "$arrayToObject": { "$map": { "input": { "$objectToArray": "$curr" }, "as": "kv", "in": { "k": "$$kv.k", "v": { "$let": { "vars": { "currVal": "$$kv.v", "preVal": { "$getField": { "field": "$$kv.k", "input": "$pre" } }, "growthVal": { "$getField": { "field": "$$kv.k", "input": "$growth" } } }, "in": { "curr": "$$currVal", "pre": "$$preVal", "growth": { "$cond": [ { "$in": ["$$kv.k", percent_fields] }, "$$growthVal", { "$round": ["$$growthVal", 1] } ] } } } } } } } } } }

def getQueriesPipeline(uid:str, marketplace: ObjectId, dates: StartEndDate):
        from dzgroshared.db.collections.pipelines.queries import GetQueries
        pipeline = GetQueries.pipeline(uid, marketplace, dates)
        pipeline.extend([{"$project": {"tag": 0, "dates": 0}}, {"$match": {"disabled": False}},{"$set": {"collatetype": CollateType.list()}}, {"$unwind": "$collatetype"}])
        pipeline.append({ "$addFields": { "currdates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$curr.startdate", "endDate": "$curr.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$curr.startdate", "unit": "day", "amount": "$$i" } } } }, "predates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$pre.startdate", "endDate": "$pre.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$pre.startdate", "unit": "day", "amount": "$$i" } } } } } } )
        pipeline.append({ '$lookup': { 'from': 'date_analytics', 'let': { 'currdates': '$currdates','predates': '$predates', 'collatetype': "$collatetype", 'dates': {"$setUnion": {"$concatArrays": ["$currdates","$predates"]}} }, 'pipeline': [ { '$match': { '$expr': { '$and': [ {"$eq": ["$uid", uid]},{"$eq": ["$marketplace", marketplace]},{"$eq": ["$collatetype", "$$collatetype"]},{ '$in': [ '$date', '$$dates' ] } ] } } }, { '$group': { '_id': { 'collatetype': '$collatetype', 'value': '$value', 'parent': '$parent' }, 'data': { '$push': '$$ROOT' } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { '$reduce': { 'input': '$data', 'initialValue': { 'curr': [], 'pre': [] }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$in': [ '$$this.date', "$$currdates" ] }, 'then': { 'curr': { '$concatArrays': [ '$$value.curr', [ '$$this.data' ] ] } }, 'else': { '$cond': { 'if': { '$in': [ '$$this.date', "$$predates" ] }, 'then': { 'pre': { '$concatArrays': [ '$$value.pre', [ '$$this.data' ] ] } }, 'else': {} } } } } ] } } } ] } } }, { '$set': { 'curr': { '$reduce': { 'input': '$curr', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } }, 'pre': { '$reduce': { 'input': '$pre', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } } } } ], 'as': 'data' } })
        pipeline.extend([{ '$unwind': { 'path': '$data', 'preserveNullAndEmptyArrays': False } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$data', { 'queryid': '$_id' } ] } } }])
        from dzgroshared.db.extras import Analytics
        pipeline.append(Analytics.addMissingFields('curr'))
        pipeline.extend(Analytics.addDerivedMetrics('curr'))
        pipeline.append(Analytics.addMissingFields('pre'))
        pipeline.extend(Analytics.addDerivedMetrics('pre'))
        pipeline.append(Analytics.addGrowth())
        pipeline.append(Analytics.create_comparison_data())
        pipeline.append({"$set": {"uid": uid, "marketplace": marketplace}})
        pipeline.extend([{"$project": {"curr": 0, "pre": 0,'growth':0}}, {"$merge": {"into":CollectionType.QUERY_RESULTS.value, "whenMatched": "merge", "whenNotMatched": "insert"}}])
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        return pipeline


# for x in AnalyticsMetric.values():
#     if x not in [c.metric for c in Analytics.MetricDetails]:
#         print(x.value)
# print("Done")
