from datetime import datetime
from typing import List, Optional, Dict, Any
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.spapi.orders import (
    GetOrdersResponse,
    GetOrderResponse,
    GetOrderItemsResponse,
)

class OrdersClient(BaseClient):
    """Client for the Orders API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_orders(
        self, marketplace_ids: List[str], created_after: Optional[str] = None, created_before: Optional[str] = None, last_updated_after: Optional[str] = None, last_updated_before: Optional[str] = None, order_statuses: Optional[List[str]] = None, fulfillment_channels: Optional[List[str]] = None, payment_methods: Optional[List[str]] = None, buyer_email: Optional[str] = None, seller_order_id: Optional[str] = None, max_results_per_page: Optional[int] = None, easy_ship_shipment_statuses: Optional[List[str]] = None, next_token: Optional[str] = None, amazon_order_ids: Optional[List[str]] = None, actual_fulfillment_supply_source_id: Optional[str] = None, is_ispu: Optional[bool] = None, store_chain_store_id: Optional[str] = None
    ) -> GetOrdersResponse:
        params: dict = {"MarketplaceIds": ",".join(marketplace_ids)}
        if created_after:
            params["CreatedAfter"] = created_after
        if created_before:
            params["CreatedBefore"] = created_before
        if last_updated_after:
            params["LastUpdatedAfter"] = last_updated_after
        if last_updated_before:
            params["LastUpdatedBefore"] = last_updated_before
        if order_statuses:
            params["OrderStatuses"] = ",".join(order_statuses)
        if fulfillment_channels:
            params["FulfillmentChannels"] = ",".join(fulfillment_channels)
        if payment_methods:
            params["PaymentMethods"] = ",".join(payment_methods)
        if buyer_email:
            params["BuyerEmail"] = buyer_email
        if seller_order_id:
            params["SellerOrderId"] = seller_order_id
        if max_results_per_page:
            params["MaxResultsPerPage"] = max_results_per_page
        if easy_ship_shipment_statuses:
            params["EasyShipShipmentStatuses"] = ",".join(easy_ship_shipment_statuses)
        if next_token:
            params["NextToken"] = next_token
        if amazon_order_ids:
            params["AmazonOrderIds"] = ",".join(amazon_order_ids)
        if actual_fulfillment_supply_source_id:
            params["ActualFulfillmentSupplySourceId"] = actual_fulfillment_supply_source_id
        if is_ispu:
            params["IsISPU"] = is_ispu
        if store_chain_store_id:
            params["StoreChainStoreId"] = store_chain_store_id
        return await self._request(
            method="GET",
            path="/orders/v0/orders",
            operation="getOrders",
            params=params,
            response_model=GetOrdersResponse,
        )

    async def get_order(self, order_id: str) -> GetOrderResponse:
        return await self._request(
            method="GET",
            path=f"/orders/v0/orders/{order_id}",
            operation="getOrder",
            response_model=GetOrderResponse,
        )

    async def get_order_items(self, order_id: str, next_token: Optional[str] = None) -> GetOrderItemsResponse:
        params = {}
        if next_token:
            params["NextToken"] = next_token
        return await self._request(
            method="GET",
            path=f"/orders/v0/orders/{order_id}/orderItems",
            operation="getOrderItems",
            params=params,
            response_model=GetOrderItemsResponse,
        ) 