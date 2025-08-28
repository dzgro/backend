from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor, LookUpPipelineMatchExpression
from dzgroshared.models.enums import CollectionType
from dzgroshared.models.model import PyObjectId


def execute(pp: PipelineProcessor, queryid: PyObjectId):
    matchstage = pp.matchMarketplace({'collatetype': 'sku', 'queryId': queryid})
    setSoldQty = pp.set({ 'soldqty': { '$ifNull': [ '$data.netquantity.curr', 0 ] } })
    filterSoldProducts = pp.match({ 'soldqty': { '$gt': 0 } })
    letkeys=['sku']
    innerpipeline = [pp.matchAllExpressions([LookUpPipelineMatchExpression(key=key) for key in letkeys]), pp.project(['quantity','sku','asin'])]
    getQuantity = pp.lookup(CollectionType.PRODUCTS,'quantity',letkeys=letkeys, pipeline=innerpipeline)
    mergeQty = pp.replaceRoot(pp.mergeObjects(["$$ROOT", pp.first('quantity')]))
    setdays = pp.set({"inventorydays": { '$toInt': { '$divide': [ '$quantity', { '$divide': [ '$soldqty', 7 ] } ] } }})
    setTag = pp.set({"inventorytag": { '$switch': { 'branches': [ { 'case': { '$or': [ { '$eq': [ '$quantity', 0 ] }, { '$eq': [ '$inventorydays', 0 ] } ] }, 'then': 'Out of Stock' }, { 'case': { '$lte': [ '$inventorydays', 7 ] }, 'then': 'Under a Week' }, { 'case': { '$lte': [ '$inventorydays', 15 ] }, 'then': '1-2 Weeks' }, { 'case': { '$lte': [ '$v', 30 ] }, 'then': '15-30 Days' }, { 'case': { '$lte': [ '$inventorydays', 60 ] }, 'then': '1-2 months' } ], 'default': 'Over 2 Months' } }})
    project = pp.project(['asin','sku','inventorydays','inventorytag','soldqty','quantity'],["_id"])
    pipeline = [matchstage, setSoldQty, filterSoldProducts, getQuantity, mergeQty,setdays, setTag, project]
    return pipeline