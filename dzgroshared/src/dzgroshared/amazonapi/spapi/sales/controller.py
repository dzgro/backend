from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dzgroshared.amazonapi.client import BaseClient
from .model import (
    GetOrderMetricsResponse,
    OrderMetricsInterval,
    Granularity,
    BuyerType,
    FirstDayOfWeek
)

class SalesClient(BaseClient):
    """Client for the Sales API."""
    dateformat = "%Y-%m-%dT%H:%M:%S.%fZ"

    async def get_order_metrics(
        self,
        interval: str,
        granularity: Granularity,
        granularity_time_zone: Optional[str] = None,
        buyer_type: Optional[BuyerType] = None,
        fulfillment_network: Optional[str] = None,
        first_day_of_week: Optional[FirstDayOfWeek] = None,
        asin: Optional[str] = None,
        sku: Optional[str] = None,
        amazon_program: Optional[str] = None
    ) -> GetOrderMetricsResponse:
        params = {
            "marketplaceIds": [self.config.marketplaceid],
            "interval": interval,
            "granularity": granularity.value
        }
        if granularity_time_zone:
            params["granularityTimeZone"] = granularity_time_zone
        if buyer_type:
            params["buyerType"] = buyer_type.value
        if fulfillment_network:
            params["fulfillmentNetwork"] = fulfillment_network
        if first_day_of_week:
            params["firstDayOfWeek"] = first_day_of_week.value
        if asin:
            params["asin"] = asin
        if sku:
            params["sku"] = sku
        if amazon_program:
            params["amazonProgram"] = amazon_program
        return await self._request(
            method="GET",
            path="/sales/v1/orderMetrics",
            operation="getOrderMetrics",
            params=params,
            response_model=GetOrderMetricsResponse
        ) 
    

    async def getLast30DaysSales(self):
        now = datetime.now()
        thirty_days_ago = (now - timedelta(days=30)).strftime(self.dateformat)
        return await self.get_order_metrics(
            interval=f"{thirty_days_ago}--{now.strftime(self.dateformat)}",
            granularity=Granularity.TOTAL
        )
