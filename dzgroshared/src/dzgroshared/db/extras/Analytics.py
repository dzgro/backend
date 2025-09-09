from typing import Literal
from bson import ObjectId
from dzgroshared.models.collections.analytics import ComparisonPeriodDataRequest, MultiLevelColumns, PeriodDataRequest
from dzgroshared.models.enums import AnalyticGroupMetricLabel, AnalyticsMetric, AnalyticsMetricOperation, CollateType, CollectionType, CountryCode
from dzgroshared.models.model import AnalyticKeyGroup, AnalyticKeylabelValue, MetricGroup, MetricItem, NestedColumn, StartEndDate
from dzgroshared.models.extras.Analytics import COMPARISON_METRICS, PERIOD_METRICS, METRIC_DETAILS, METRIC_CALCULATIONS, MONTH_BARS, MONTH_METER_GROUPS, MONTH_DATA, PERIOD_METRICS, STATE_DETAILED_METRICS, STATE_LITE_METRICS, ALL_STATE_METRICS, MONTH_METRICS, MONTH_DATE_METRICS
SchemaType = Literal['Period','Comparison','Month Meters', 'Month Bars', 'Month Data', 'State Lite', 'State Detail', 'State All', 'Month', 'Month Date']

GroupBySchema: dict[SchemaType, list[MetricGroup]] = {
    'Period': PERIOD_METRICS,
    'Comparison': COMPARISON_METRICS,
    'Month Meters': MONTH_METER_GROUPS,
    'Month Bars': [MONTH_BARS],
    'Month Data': [MONTH_DATA],
    'Month': MONTH_METRICS,
    'Month Date': MONTH_DATE_METRICS,
    'State Lite': STATE_LITE_METRICS,
    'State Detail': STATE_DETAILED_METRICS,
    'State All': ALL_STATE_METRICS,
}


def getSchema(schemaType: SchemaType, collatetype: CollateType) -> list[dict]:
    groups = getMetricGroupsBySchemaType(schemaType, collatetype)
    return [s.model_dump(mode="json") for s in groups]

def transformData(schemaType: SchemaType, data: list[dict], collatetype: CollateType, countryCode: CountryCode):
    schema = getSchema(schemaType, collatetype)
    if schemaType=='Comparison':
        return [{**d, "data": [transformComparisonData(s, d['data'], countryCode, 1) for s in schema]} for d in data]
    elif schemaType == 'State All':
        return transformStateAllData(GroupBySchema[schemaType], data, countryCode)
    elif schemaType == 'Month Date':
        return transformMonthDateData(GroupBySchema[schemaType], data, countryCode)
    elif schemaType == 'Month' or schemaType == 'State Detail':
        return transformSchemaData(GroupBySchema[schemaType], data, countryCode)
    else: return [{**d, "data": [transformPeriodData(s, d['data'], countryCode, 1) for s in schema]} for d in data]


def getMetricGroupsBySchemaType(schemaType: SchemaType, collatetype: CollateType) -> list[MetricGroup]:
    groups = GroupBySchema[schemaType]
    if collatetype==CollateType.SKU: return [g for g in groups if g.metric!=AnalyticGroupMetricLabel.TRAFFIC]
    return groups

percent_fields = [d.metric.value for d in METRIC_DETAILS if d.ispercentage]
non_percent_fields = [d.metric.value for d in METRIC_DETAILS if not d.ispercentage]

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
        detail = next((d for d in METRIC_DETAILS if d.metric == key), None)
        if detail:
            result['label'] = schema.get('label', None)
            if not result['label']: result['label'] = detail.label
            result['description'] = detail.description
        else: 
            result['label'] = schema['metric']
        result["value"] = round(value,2) if isinstance(value, float) else value
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
            detail = next((d for d in METRIC_DETAILS if d.metric == key), None)
            if detail:
                result['label'] = schema.get('label', None)
                if not result['label']: result['label'] = detail.label
                result['description'] = detail.description
                for k,v in value.items():
                    result[k] = {
                        "value": round(v,2) if isinstance(v, float) else v,
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

def transformMonthDateData(schema: list[MetricGroup], data: list[dict], countrycode: CountryCode):
    metrics: list[AnalyticsMetric] = [ss.metric for s in schema for ss in s.items]
    result: list[dict] = []
    for metric in metrics:
        for item in data:
            value = item['data'].get(metric.value, None)
            index = next((i for i, d in enumerate(result) if d['date']==item['date']), None)
            if index is None:
                result.append({"date": item['date'], 'values': []})
                index = len(result)-1
            result[index]['values'].append({
                "value": round(value,2) if isinstance(value, float) else value,
                "valueString": format_number(value, metric, countrycode)
            })
    return result

def transformStateAllData(schema: list[MetricGroup], data: list[dict], countrycode: CountryCode):
    metrics: list[AnalyticsMetric] = []
    for s in schema:
        for ss in (s.items or []):
            if not s.items: # single level
                metrics.append(ss.metric)
                continue
            for sss in (ss.items or []):
                metrics.append(sss.metric)
    result: list[dict] = []
    for metric in metrics:
        for item in data:
            value = item['data'].get(metric.value, None)
            index = next((i for i, d in enumerate(result) if d['state']==item['state']), None)
            if index is None:
                result.append({"state": item['state'], 'values': []})
                index = len(result)-1
            result[index]['values'].append({
                "value": round(value,2) if isinstance(value, float) else value,
                "valueString": format_number(value, metric, countrycode)
            })
    return result

def transformSchemaData(schema: list[MetricGroup], data: list[dict], countrycode: CountryCode):
    def getResultItem(metric: MetricItem):
        try:
            detail = next((d for d in METRIC_DETAILS if d.metric == metric.metric), None)
            if not detail: raise ValueError(f"Metric detail not found for {metric.metric}")
            result: dict = {"label": metric.label or detail.label, "values": [], "description": detail.description, "items": []}
            for item in data:
                value = item['data'].get(metric.metric.value, None)
                result['values'].append({
                    "value": round(value,2) if isinstance(value, float) else value,
                    "valueString": format_number(value, metric.metric, countrycode)
                })
            return result
        except Exception as e:
            print(e)
            raise e

    result: list[dict] = []
    for s in schema:
        resultItem: dict = {"label": s.metric.value, "items": []}
        for ss in (s.items or []):
            ssItem = getResultItem(ss)
            for sss in (ss.items or []):
                sssItem = getResultItem(sss)
                for ssss in (sss.items or []):
                    ssssItem = getResultItem(ssss)
                    sssItem["items"].append(ssssItem)
                ssItem["items"].append(sssItem)
            resultItem["items"].append(ssItem)
        result.append(resultItem)
    return result



def addDerivedMetrics(data_key: str = "data"):
    level0: dict = {}
    level1: dict = {}
    level2: dict = {}
    level3: dict = {}
    level4: dict = {}
    level5: dict = {}
    dk = f"${data_key}."
    for item in METRIC_CALCULATIONS:
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
            level0.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 1:
            level1.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 2:
            level2.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 3:
            level3.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 4:
            level4.update( {f"{data_key}.{item.metric.value}": result} )
        elif item.level == 5:
            level5.update( {f"{data_key}.{item.metric.value}": result} )
    return [ { "$addFields": level0 },{ "$addFields": level1 }, { "$addFields": level2 }, { "$addFields": level3 }, { "$addFields": level4 }, { "$addFields": level5 }]

def addGrowth():
    return { "$addFields": { "growth": { "$arrayToObject": { "$map": { "input": { "$objectToArray": "$curr" }, "as": "kv", "in": { "k": "$$kv.k", "v": { "$let": { "vars": { "currVal": "$$kv.v", "preVal": { "$getField": { "field": "$$kv.k", "input": "$pre" } }, "percentFields": percent_fields }, "in": { "$cond": [ { "$in": ["$$kv.k", "$$percentFields"] }, { "$cond": [ { "$lt": [{ "$abs": { "$subtract": ["$$currVal", "$$preVal"] } }, 10] }, { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 2] }, { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 1] } ] }, { "$cond": [ { "$or": [{ "$eq": ["$$preVal", 0] }, { "$eq": ["$$preVal", None] }] }, 0, { "$cond": [ { "$lt": [ { "$abs": { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] } }, 10 ] }, { "$round": [ { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] }, 2 ] }, { "$round": [ { "$multiply": [ { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] }, 100 ] }, 1 ] } ] } ] } ] } } } } } } } } }

def create_comparison_data():
    return { "$addFields": { "data": { "$arrayToObject": { "$map": { "input": { "$objectToArray": "$curr" }, "as": "kv", "in": { "k": "$$kv.k", "v": { "$let": { "vars": { "currVal": "$$kv.v", "preVal": { "$getField": { "field": "$$kv.k", "input": "$pre" } }, "growthVal": { "$getField": { "field": "$$kv.k", "input": "$growth" } } }, "in": { "curr": "$$currVal", "pre": "$$preVal", "growth": { "$cond": [ { "$in": ["$$kv.k", percent_fields] }, "$$growthVal", { "$round": ["$$growthVal", 1] } ] } } } } } } } } } }

def getQueriesPipeline(marketplace: ObjectId, dates: StartEndDate):
        from dzgroshared.db.collections.pipelines.queries import GetQueries
        pipeline = GetQueries.pipeline(marketplace, dates)
        pipeline.extend([{"$project": {"tag": 0, "dates": 0}}, {"$match": {"disabled": False}},{"$set": {"collatetype": CollateType.list()}}, {"$unwind": "$collatetype"}])
        pipeline.append({ "$addFields": { "currdates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$curr.startdate", "endDate": "$curr.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$curr.startdate", "unit": "day", "amount": "$$i" } } } }, "predates": { "$map": { "input": { "$range": [ 0, { "$add": [ { "$dateDiff": { "startDate": "$pre.startdate", "endDate": "$pre.enddate", "unit": "day" } }, 1 ] } ] }, "as": "i", "in": { "$dateAdd": { "startDate": "$pre.startdate", "unit": "day", "amount": "$$i" } } } } } } )
        pipeline.append({ '$lookup': { 'from': 'date_analytics', 'let': { 'currdates': '$currdates','predates': '$predates', 'collatetype': "$collatetype", 'dates': {"$setUnion": {"$concatArrays": ["$currdates","$predates"]}} }, 'pipeline': [ { '$match': { '$expr': { '$and': [ {"$eq": ["$marketplace", marketplace]},{"$eq": ["$collatetype", "$$collatetype"]},{ '$in': [ '$date', '$$dates' ] } ] } } }, { '$group': { '_id': { 'collatetype': '$collatetype', 'value': '$value', 'parent': '$parent' }, 'data': { '$push': '$$ROOT' } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { '$reduce': { 'input': '$data', 'initialValue': { 'curr': [], 'pre': [] }, 'in': { '$mergeObjects': [ '$$value', { '$cond': { 'if': { '$in': [ '$$this.date', "$$currdates" ] }, 'then': { 'curr': { '$concatArrays': [ '$$value.curr', [ '$$this.data' ] ] } }, 'else': { '$cond': { 'if': { '$in': [ '$$this.date', "$$predates" ] }, 'then': { 'pre': { '$concatArrays': [ '$$value.pre', [ '$$this.data' ] ] } }, 'else': {} } } } } ] } } } ] } } }, { '$set': { 'curr': { '$reduce': { 'input': '$curr', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } }, 'pre': { '$reduce': { 'input': '$pre', 'initialValue': {}, 'in': { '$arrayToObject': { '$filter': { 'input': { '$map': { 'input': { '$setUnion': [ { '$map': { 'input': { '$objectToArray': '$$value' }, 'as': 'v', 'in': '$$v.k' } }, { '$map': { 'input': { '$objectToArray': '$$this' }, 'as': 't', 'in': '$$t.k' } } ] }, 'as': 'key', 'in': { 'k': '$$key', 'v': { '$round': [ { '$add': [ { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$value' } }, 0 ] }, { '$ifNull': [ { '$getField': { 'field': '$$key', 'input': '$$this' } }, 0 ] } ] }, 2 ] } } } }, 'as': 'item', 'cond': { '$ne': [ '$$item.v', 0 ] } } } } } } } } ], 'as': 'data' } })
        pipeline.extend([{ '$unwind': { 'path': '$data', 'preserveNullAndEmptyArrays': False } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$data', { 'queryid': '$_id' } ] } } }])
        from dzgroshared.db.extras import Analytics
        pipeline.append(addMissingFields('curr'))
        pipeline.extend(addDerivedMetrics('curr'))
        pipeline.append(addMissingFields('pre'))
        pipeline.extend(addDerivedMetrics('pre'))
        pipeline.append(addGrowth())
        pipeline.append(create_comparison_data())
        pipeline.append({"$set": {"marketplace": marketplace}})
        pipeline.extend([{"$project": {"curr": 0, "pre": 0,'growth':0}}, {"$merge": {"into":CollectionType.QUERY_RESULTS.value, "whenMatched": "merge", "whenNotMatched": "insert"}}])
        from dzgroshared.utils import mongo_pipeline_print
        mongo_pipeline_print.copy_pipeline(pipeline)
        return pipeline


def getAllMetricsInGroup(groups: list[MetricGroup]) -> list[AnalyticsMetric]:
    metrics: list[AnalyticsMetric] = []
    for group in groups:
        for item in group.items:
            metrics.append(item.metric)
            for subitem in (item.items or []):
                metrics.append(subitem.metric)
                for subsubitem in (subitem.items or []):
                    metrics.append(subsubitem.metric)
    return metrics

def getMetricGroupsProjection(schemaType: SchemaType, collateType: CollateType):
    groups = getMetricGroupsBySchemaType(schemaType, collateType)
    metrics = getAllMetricsInGroup(groups)
    return [metric.value for metric in metrics]

def getProjectionStage(schemaType: SchemaType, collateType: CollateType):
    projection = getMetricGroupsProjection(schemaType, collateType)
    return { '$set': { 'data': { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$data' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': { 'if': { '$in': [ '$$this.k', projection ] }, 'then': [ '$$this' ], 'else': [] } } ] } } } } } }

def getAnalyticsGroups():
    data: list[AnalyticKeyGroup] = []
    for val in AnalyticGroupMetricLabel.values():
        keys: list[AnalyticsMetric] = []
        periodGroup = next((g for g in PERIOD_METRICS if g.metric==val), None)
        comparisonGroup = next((g for g in COMPARISON_METRICS if g.metric==val), None)
        if periodGroup:
            keys.extend(getAllMetricsInGroup([periodGroup]))
        if comparisonGroup:
            keys.extend(getAllMetricsInGroup([comparisonGroup]))
        keys = list(set(keys))
        metrics: list[AnalyticKeylabelValue] = []
        for k in keys:
            label = next((d.label for d in METRIC_DETAILS if d.metric==k), None)
            if label:
                metrics.append(AnalyticKeylabelValue(label=label, value=k))
        data.append(AnalyticKeyGroup(label=val, items=metrics))
    return data

def convertSchemaToMetricItemList(schemaType: SchemaType):

    def convertToLabel(metric: MetricItem):
        try:
            detail = next((d for d in METRIC_DETAILS if d.metric == metric.metric), None)
            if not detail: raise ValueError(f"Metric detail not found for {metric.metric}")
            result =  MetricItem(metric=metric.metric, label=metric.label or detail.label)
            if metric.items: result.items = [convertToLabel(s) for s in metric.items]
            return result
        except Exception as e:
            raise e

    return [convertToLabel(x) for s in GroupBySchema[schemaType] for x in s.items]

def convertSchematoMultiLevelColumns(schemaType: SchemaType) -> MultiLevelColumns:
    metrics = convertSchemaToMetricItemList(schemaType)
    columns1 = [NestedColumn(header=m.label or m.metric.value, colSpan=len(m.items or [])) for m in metrics]
    columns2 = [NestedColumn(header=x.label or x.metric.value, colSpan=1) for m in metrics for x in (m.items or [])]
    columns3 = [NestedColumn(header=y.label or y.metric.value, colSpan=1) for m in metrics for x in (m.items or []) for y in (x.items or [])]
    if not columns3: columns3 = None
    return MultiLevelColumns(columns1=columns1, columns2=columns2, columns3=columns3)



# for x in AnalyticsMetric.values():
#     if x not in [c.metric for c in MetricDetails]:
#         print(x.value)
# print("Done")
