from bson import ObjectId
from datetime import datetime, timedelta
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.enums import CollectionType
from dzgroshared.db.model import Sort, Paginator
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.orders.model import (
    OrderPaymentDetail, OrderPaymentRequest, OrderPaymentList, OrderPaymentFacets, OrderPaymentFacetRequest
)
from dzgroshared.db.orders.pipelines import GetOrderWithSettlements
from dzgroshared.db.orders.pipelines import GetOrderSettlementFacets

class OrdersHelper:
    client: DzgroSharedClient
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.ORDERS), marketplace=client.marketplaceId)

    async def getOrderPayments(self, req: OrderPaymentRequest) -> OrderPaymentList:
        marketplace = await self.client.db.marketplaces.getUserMarketplace(self.client.marketplace.id)
        pipeline, dates = GetOrderWithSettlements.pipelineForList(marketplace, req)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Orders found")
        return OrderPaymentList.model_validate({**data[0], "dates": dates})

    async def getOrderPaymentDetailById(self, orderid: str) -> OrderPaymentDetail:
        marketplace = await self.client.db.marketplaces.getUserMarketplace(self.client.marketplace.id)
        pipeline = GetOrderWithSettlements.pipelineForOrderId(marketplace, orderid)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Orders found")
        return OrderPaymentDetail.model_validate(data[0])

    async def getOrderPaymentFacets(self, req: OrderPaymentFacetRequest) -> OrderPaymentFacets:
        marketplace = await self.client.db.marketplaces.getUserMarketplace(self.client.marketplace.id)
        pipeline = GetOrderSettlementFacets.pipeline(marketplace, req)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Orders found")
        return OrderPaymentFacets.model_validate(data[0])
        