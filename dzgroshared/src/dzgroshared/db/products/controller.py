from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollectionType
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.products.model import ProductView

class ProductHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.PRODUCTS), marketplace=client.marketplaceId)

    async def getSku(self, sku: str):
        return await self.db.findOne({"sku": sku}, projectionInc=list(ProductView.model_fields.keys()), projectionExc=["_id"])

    async def getAsin(self, asin: str):
        return await self.db.findOne({"asin": asin}, projectionInc=list(ProductView.model_fields.keys()), projectionExc=["_id"])

    async def getSkus(self, skus: list[str]):
        return await self.db.find({"sku": {"$in": skus}}, projectionInc=list(ProductView.model_fields.keys()), projectionExc=["_id"])

    async def getAsins(self, asins: list[str]):
        return await self.db.find({"asin": {"$in": asins}}, projectionInc=list(ProductView.model_fields.keys()), projectionExc=["_id"])

    async def getParentSku(self, parentsku: str):
        from .pipelines import GetParentSku
        pipeline = GetParentSku.pipeline(self.client.marketplaceId, parentsku)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Product not found")
        return data[0]
        

    
