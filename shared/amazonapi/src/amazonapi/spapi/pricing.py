from typing import List, Optional, Dict, Any
from amazonapi.client import BaseClient
from models.amazonapi.spapi.pricing import (
    GetPricingResponse,
)

class PricingClient(BaseClient):
    """Client for the Product Pricing API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_pricing(
        self, marketplace_id: str, item_type: str, asins: Optional[List[str]] = None, skus: Optional[List[str]] = None, item_condition: Optional[str] = None
    ) -> GetPricingResponse:
        params = {"MarketplaceId": marketplace_id, "ItemType": item_type}
        if asins:
            params["Asins"] = ",".join(asins)
        if skus:
            params["Skus"] = ",".join(skus)
        if item_condition:
            params["ItemCondition"] = item_condition
        return await self._request(
            method="GET",
            path="/products/pricing/v0/pricing",
            operation="getPricing",
            params=params,
            response_model=GetPricingResponse,
        ) 