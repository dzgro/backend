# from app.HelperModules.Helpers.Date import DateHelper
# from app.routers.analytics.orders.model import OrdersQuery, OrderResult
# from app.routers.sellers.models import Marketplace
# from app.HelperModules.Db import mongo_db

# class OrderPipeline:
#     def __init__(self, marketplace: Marketplace) -> None:
#         self.marketplace = marketplace
#         self.collection = mongo_db.orders
#         self.timezone = DateHelper()

#     def getResults(self,query: OrdersQuery):
#         try:
#             count = 0
#             if not query.orderId:
#                 countResult = self.count(query)
#                 count = countResult[0]['count'] if len(countResult) > 0 else 0
#             orders = self.getOrders(query)
#             if query.orderId: count = len(orders)
#             if not query.loadfilters: return {"orders": orders, "count": count}
#             filterResult = self.getFilters()
#             q = query.model_dump()
#             filters = {k: {"applied": q[k] or [], "values": v} for k,v in filterResult[0].items()}
#             return {"orders": orders, "filters": filters, "count": count}
#         except Exception as e:
#             print(e)
#             return {"orders": [], "filters": {"status": [], "fulfillment": [], "months": []}, "count": 0}
    
#     def getMatchPipeline(self, query: OrdersQuery):
#             matchPipeline: dict = {'marketplace': self.marketplace.id}
#             if query.status: matchPipeline['status'] = {"$in": query.status}
#             if query.fulfillment: matchPipeline['fulfillment'] = {"$in": query.fulfillment}
#             if query.months: matchPipeline['$expr'] = {"$in": [{"$dateToString": {"date": "$date","timezone": self.marketplace.detail.timezone,"format": "%b-%Y"}},query.months]}
#             return {"$match": matchPipeline}
    
#     def setDate(self):
#          return {"$set": {"date": {"$dateFromString": {"dateString": {'$dateToString': {'date': '$date', 'timezone': self.marketplace.detail.timezone}}}}}}

#     def getFilters(self):
#         return list(self.collection.aggregate([ { '$match': { 'marketplace': self.marketplace.id } },{ '$group': { '_id': '$orderId', 'date': { '$first': '$date' }, 'fulfillment': { '$first': '$fulfillment' }, 'status': { '$first': '$status' } } }, { '$facet': { 'status': [ { '$sortByCount': '$status' } ], 'months': [ { '$sortByCount': { '$dateToString': { 'date': '$date', 'timezone': 'Asia/Kolkata', 'format': '%b-%Y' } } } ], 'fulfillment': [ { '$sortByCount': '$fulfillment' } ] } }, ]))

    
#     def count(self, query: OrdersQuery):
#         pipeline = [self.getMatchPipeline(query), {"$count": "count"}]
#         return list(self.collection.aggregate(pipeline=pipeline))
    
#     def getOrders(self, query: OrdersQuery):
#         pipeline = [ self.getMatchPipeline(query),self.setDate(), {'$sort': {'date': -1} },{ '$skip': query.paginator.skip }, { '$limit': query.paginator.limit }, { '$addFields': { 'details': { '$let': { 'vars': { 'cancelled': { '$eq': [ '$status', 'Cancelled' ] }, 'quantity': { '$subtract': [ '$quantity', '$returnQuantity' ] }, 'isReturned': { '$eq': [ { '$subtract': [ '$quantity', '$returnQuantity' ] }, 0 ] }, 'sp': { '$ifNull': [ '$shippingPrice', 0 ] }, 'st': { '$ifNull': [ '$shippingTax', 0 ] }, 'gwp': { '$ifNull': [ '$giftWrapPrice', 0 ] }, 'gwt': { '$ifNull': [ '$giftWrapTax', 0 ] }, 'spd': { '$ifNull': [ '$shipPromotionDiscount', 0 ] }, 'ipd': { '$ifNull': [ '$itemPromotionDiscount', 0 ] } }, 'in': { 'revenue': { '$cond': [ '$$isReturned', 0, { '$subtract': [ { '$add': [ '$price', '$$sp', '$$gwp' ] }, { '$add': [ '$$spd', '$$ipd' ] } ] } ] }, 'expenses': { '$sum': [ '$fees', '$shipping' ] } } } } } }, { '$group': { '_id': '$orderId', 'revenue': { '$sum': '$$ROOT.details.revenue' }, 'expenses': { '$sum': '$$ROOT.details.expenses' }, 'date': { '$first': '$$ROOT.date' }, 'fulfillment': { '$first': '$$ROOT.fulfillment' }, 'status': { '$first': '$$ROOT.status' } } }, { '$addFields': { 'orderId': '$_id', 'netProceeds': { '$sum': [ '$$ROOT.revenue', '$$ROOT.expenses' ] } } }, { '$addFields': { 'netProceedsPercent': { '$cond': [ { '$eq': [ '$revenue', 0 ] }, 0, { '$round': [ { '$multiply': [ { '$divide': [ '$netProceeds', '$revenue' ] }, 100 ] }, 1 ] } ] } } }, { '$project': { '_id': 0 } }, { '$replaceRoot': { 'newRoot': { '$arrayToObject': { '$reduce': { 'input': { '$objectToArray': '$$ROOT' }, 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$in': [ { '$type': '$$this.v' }, [ 'double', 'long', 'decimal' ] ] }, [ { 'k': '$$this.k', 'v': { '$round': [ '$$this.v', 2 ] } } ], [ '$$this' ] ] } ] } } } } } } ]
#         return list(self.collection.aggregate(pipeline=pipeline))
        
    
#     def getOrdersItems(self, orderId: str):
#             pipeline = [ { '$match': { 'marketplace': self.marketplace.id, 'orderId': orderId } }, { '$group': { '_id': '$orderId', 'date': { '$first': '$$ROOT.date' }, 'status': { '$first': '$$ROOT.status' }, 'items': { '$push': '$$ROOT' } } }, { '$lookup': { 'from': 'settlements', 'localField': '_id', 'foreignField': 'order-id', 'as': 'settlement' } }, { '$lookup': { 'from': 'products', 'let': { 'asins': { '$reduce': { 'input': '$items', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ '$$this.asin' ] ] } } } }, 'pipeline': [ { '$match': { '$expr': { '$in': [ '$asin', '$$asins' ] } } }, { '$project': { '_id': 0, 'asin': 1, 'imageUrl': 1 } } ], 'as': 'products' } }, { '$set': { 'items': { '$map': { 'input': '$items', 'as': 'item', 'in': { 'imageUrl': { '$getField': { 'input': { '$first': { '$filter': { 'input': '$products', 'as': 'p', 'cond': { '$eq': [ '$$p.asin', '$$item.asin' ] } } } }, 'field': 'imageUrl' } }, 'asin': '$$item.asin', 'sku': '$$item.sku', 'quantity': "$$item.quantity", 'price': { 'shippingPrice': { '$ifNull': [ '$$item.shippingPrice', 0 ] }, 'shippingTax': { '$ifNull': [ '$$item.shippingTax', 0 ] }, 'giftWrapPrice': { '$ifNull': [ '$$item.giftWrapPrice', 0 ] }, 'giftWrapTax': { '$ifNull': [ '$$item.giftWrapTax', 0 ] }, 'shipPromotionDiscount': { '$ifNull': [ '$$item.shipPromotionDiscount', 0 ] }, 'itemPromotionDiscount': { '$ifNull': [ '$$item.itemPromotionDiscount', 0 ] }, 'productTax': '$$item.tax', 'productPrice': { '$subtract': [ '$$item.price', '$$item.tax' ] } }, 'settlement': { '$filter': { 'input': '$settlement', 'as': 's', 'cond': { '$cond': [ { '$eq': [ { '$ifNull': [ '$$item.orderItemId', None ] }, None ] }, { '$eq': [ '$$s.sku', '$$item.sku' ] }, { '$eq': [ '$$s.order-item-code', '$$item.orderItemId' ] } ] } } } } } } } }, { '$set': { 'items': { '$map': { 'input': '$items', 'as': 'item', 'in': { '$mergeObjects': [ '$$item', { 'settlement': { '$reduce': { 'input': '$$item.settlement', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.title', '$$this.amount-type' ] }, -1 ] }, [ { 'title': '$$this.amount-type', 'items': { '$let': { 'vars': { 'values': { '$filter': { 'input': '$$item.settlement', 'as': 'f', 'cond': { '$eq': [ '$$this.amount-type', '$$f.amount-type' ] } } } }, 'in': { '$sortArray': { 'input': { '$reduce': { 'input': '$$values', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', { '$cond': [ { '$eq': [ { '$indexOfArray': [ '$$value.title', '$$this.amount-description' ] }, -1 ] }, [ { '$mergeObjects': [ { 'title': '$$this.amount-description' }, { '$reduce': { 'input': { '$filter': { 'input': '$$values', 'as': 'v', 'cond': { '$eq': [ '$$v.amount-description', '$$this.amount-description' ] } } }, 'initialValue': {}, 'in': { '$mergeObjects': [ '$$value', { '$arrayToObject': [ [ { 'k': { '$toLower': '$$this.transaction-type' }, 'v': '$$this.amount' } ] ] } ] } } } ] } ], [] ] } ] } } }, 'sortBy': { 'title': 1 } } } } } } ], [] ] } ] } } } } ] } } } } }, { '$set': { 'items': { '$reduce': { 'input': '$items', 'initialValue': [], 'in': { '$concatArrays': [ '$$value', [ { '$mergeObjects': [ '$$this', { 'settlement': { '$reduce': { 'input': '$$this.settlement', 'initialValue': [], 'in': { '$let': { 'vars': { 'title': { '$cond': [ { '$eq': [ '$$this.title', 'ItemPrice' ] }, 'Principal & Tax', { '$cond': [ { '$eq': [ '$$this.title', 'ItemFees' ] }, 'Fees', 'Other Charges' ] } ] } }, 'in': { '$let': { 'vars': { 'title': '$$title', 'idx': { '$indexOfArray': [ '$$value.title', '$$title' ] } }, 'in': { '$cond': [ { '$eq': [ '$$idx', -1 ] }, { '$concatArrays': [ '$$value', [ { 'title': '$$title', 'items': '$$this.items' } ] ] }, { '$map': { 'input': '$$value', 'as': 'v', 'in': { '$cond': [ { '$ne': [ '$$v.title', 'Other Charges' ] }, '$$v', { '$mergeObjects': [ '$$v', { 'items': { '$concatArrays': [ '$$v.items', '$$this.items' ] } } ] } ] } } } ] } } } } } } } } ] } ] ] } } } } }, { '$set': { 'settlement': { '$arrayToObject': { '$reduce': { 'input': { '$filter': { 'input': '$settlement', 'as': 's', 'cond': { '$eq': [ { '$ifNull': [ '$$s.sku', None ] }, None ] } } }, 'initialValue': [], 'in': { '$let': { 'vars': { 'amountDescription': '$$this.amount-description', 'amount': '$$this.amount' }, 'in': { '$concatArrays': [ '$$value', [ { 'k': '$$amountDescription', 'v': '$$amount' } ] ] } } } } } } } }, { '$set': { 'orderId': '$_id' } }, { '$project': { 'products': 0, '_id': 0 } } ]
#             return list(self.collection.aggregate(pipeline=pipeline))

from bson import ObjectId
from db.DbUtils import DbManager
from models.enums import CollectionType
from motor.motor_asyncio import AsyncIOMotorDatabase

class OrdersHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str
    
    def __init__(self, db: AsyncIOMotorDatabase, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(db.get_collection(CollectionType.ORDERS), uid, marketplace)

    async def replaceStateNames(self):
        matchStage = { '$match': { 'uid': self.uid, 'marketplace': self.marketplace} }
        setAlias = { '$set': { 'alias': { '$concat': [ '$country', '_', { '$toLower': '$state' } ] } } }
        lookup = { '$lookup': { 'from': 'state_names', 'localField': 'alias', 'foreignField': '_id', 'pipeline': [ { '$project': { 'state': 1, '_id': 0 } } ], 'as': 'result' } }
        filterResults = { '$match': { '$expr': { '$gt': [ { '$size': '$result' }, 0 ] } } }
        setState = { '$set': { 'state': { '$let': { 'vars': { 'state': { '$getField': { 'input': { '$arrayElemAt': [ '$result', 0 ] }, 'field': 'state' } } }, 'in': { '$ifNull': [ '$$state', '$state' ] } } } } }
        unsetField = { '$unset': [ 'result', 'alias' ] }
        merge = {"$merge": CollectionType.ORDERS.value}
        pipeline = [matchStage,setAlias,lookup,filterResults,setState,unsetField,merge]
        await self.db.aggregate(pipeline)



