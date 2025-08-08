from bson import ObjectId
from db.PipelineProcessor import LookUpPipelineMatchExpression, PipelineProcessor
from models.enums import CollectionType

class InventoryProcessor:
    pp: PipelineProcessor

    def __init__(self, pp: PipelineProcessor):
        self.pp = pp

    def execute(self):
        matchstage = self.pp.matchMarketplace({'type': 'sku', 'queryId': ObjectId('682dd88a3cf01de1a57b6166')})
        setSoldQty = self.pp.set({ 'soldqty': { '$ifNull': [ '$data.netquantity.curr', 0 ] } })
        filterSoldProducts = self.pp.match({ 'soldqty': { '$gt': 0 } })
        letkeys=['uid','marketplace','sku']
        innerpipeline = [self.pp.matchAllExpressions([LookUpPipelineMatchExpression(key=key) for key in letkeys]), self.pp.project(['quantity'])]
        getQuantity = self.pp.lookup(CollectionType.PRODUCTS,'quantity',letkeys=letkeys, pipeline=innerpipeline)
        mergeQty = self.pp.replaceRoot(self.pp.mergeObjects(["$$ROOT", self.pp.first('quantity')]))
        setdays = self.pp.set({"inventorydays": { '$toInt': { '$divide': [ '$quantity', { '$divide': [ '$soldqty', 7 ] } ] } }})
        setTag = self.pp.set({"inventorytag": { '$switch': { 'branches': [ { 'case': { '$eq': [ '$quantity', 0 ] }, 'then': 'Out of Stock' }, { 'case': { '$eq': [ '$inventorydays', 0 ] }, 'then': 'Out of Stock' }, { 'case': { '$lte': [ '$inventorydays', 7 ] }, 'then': 'Under A Week' }, { 'case': { '$lte': [ '$inventorydays', 15 ] }, 'then': '1-2 Weeks' }, { 'case': { '$lte': [ '$v', 30 ] }, 'then': '15-30 Days' }, { 'case': { '$lte': [ '$inventorydays', 60 ] }, 'then': '1-2 months' } ], 'default': 'Over 2 Months' } }})
        project = self.pp.project(['asin','sku','inventorydays','inventorytag','soldqty','quantity'],["_id"])
        pipeline = [matchstage, setSoldQty, filterSoldProducts, getQuantity, mergeQty,setdays, setTag, project]
        return pipeline
    
    def getInventoryGroups(self):
        pipeline = self.execute()
        return pipeline