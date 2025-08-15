from bson import ObjectId
from db.PipelineProcessor import PipelineProcessor, LookUpPipelineMatchExpression
from models.enums import CollectionType


def execute(pp: PipelineProcessor, queryid: str):
    matchstage = pp.matchMarketplace({'type': 'sku', 'queryId': ObjectId(queryid)})
    setSoldQty = pp.set({ 'soldqty': { '$ifNull': [ '$data.netquantity.curr', 0 ] } })
    filterSoldProducts = pp.match({ 'soldqty': { '$gt': 0 } })
    letkeys=['uid','marketplace','sku']
    innerpipeline = [pp.matchAllExpressions([LookUpPipelineMatchExpression(key=key) for key in letkeys]), pp.project(['quantity'])]
    getQuantity = pp.lookup(CollectionType.PRODUCTS,'quantity',letkeys=letkeys, pipeline=innerpipeline)
    mergeQty = pp.replaceRoot(pp.mergeObjects(["$$ROOT", pp.first('quantity')]))
    setdays = pp.set({"inventorydays": { '$toInt': { '$divide': [ '$quantity', { '$divide': [ '$soldqty', 7 ] } ] } }})
    setTag = pp.set({"inventorytag": { '$switch': { 'branches': [ { 'case': { '$eq': [ '$quantity', 0 ] }, 'then': 'Out of Stock' }, { 'case': { '$eq': [ '$inventorydays', 0 ] }, 'then': 'Out of Stock' }, { 'case': { '$lte': [ '$inventorydays', 7 ] }, 'then': 'Under A Week' }, { 'case': { '$lte': [ '$inventorydays', 15 ] }, 'then': '1-2 Weeks' }, { 'case': { '$lte': [ '$v', 30 ] }, 'then': '15-30 Days' }, { 'case': { '$lte': [ '$inventorydays', 60 ] }, 'then': '1-2 months' } ], 'default': 'Over 2 Months' } }})
    project = pp.project(['asin','sku','inventorydays','inventorytag','soldqty','quantity'],["_id"])
    pipeline = [matchstage, setSoldQty, filterSoldProducts, getQuantity, mergeQty,setdays, setTag, project]
    return pipeline