from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class ProductHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.PRODUCTS), uid, marketplace)


    async def getSku(self, sku: str):
        return await self.db.findOne({"sku": sku})

    async def getAsin(self, asin: str):
        return self.db.findOne({"asin": asin})

    async def getSkus(self, skus: list[str]):
        return await self.db.find({"sku": {"$in": skus}})

    async def getAsins(self, asins: list[str]):
        return await self.db.find({"asin": {"$in": asins}})
    
    async def getParentSku(self, parentsku: str):
        pipeline = [self.db.pp.matchMarketplace({'sku': parentsku}),{ '$lookup': { 'from': 'products', 'let': { 'uid': '$uid', 'marketplace': '$marketplace', 'skus': '$childskus' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$uid', '$$uid' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$in': [ '$sku', '$$skus' ] } ] } } } ], 'as': 'children' } } ]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Product not found")
        return data[0]
        

    
