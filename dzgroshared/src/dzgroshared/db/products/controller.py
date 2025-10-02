from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.products.model import SkuView, AsinView

class ProductHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PRODUCTS), marketplace=client.marketplaceId)

    async def getSku(self, sku: str):
        return await self.db.findOne({"sku": sku}, projectionInc=list(SkuView.model_fields.keys()), projectionExc=["_id"])

    async def getAsin(self, asin: str):
        return await self.db.findOne({"asin": asin}, projectionInc=list(AsinView.model_fields.keys()), projectionExc=["_id"])

    async def getSkus(self, skus: list[str]):
        return await self.db.find({"sku": {"$in": skus}}, projectionInc=list(SkuView.model_fields.keys()), projectionExc=["_id"])

    async def getAsins(self, asins: list[str]):
        return await self.db.find({"asin": {"$in": asins}}, projectionInc=list(AsinView.model_fields.keys()), projectionExc=["_id"])

    async def getParentSku(self, parentsku: str):
        pipeline = [self.db.pp.matchMarketplace({'sku': parentsku}),{ '$lookup': { 'from': 'products', 'let': { 'marketplace': '$marketplace', 'skus': '$childskus' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$marketplace', '$$marketplace' ] }, { '$in': [ '$sku', '$$skus' ] } ] } } } ], 'as': 'children' } } ]
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Product not found")
        return data[0]
        

    
