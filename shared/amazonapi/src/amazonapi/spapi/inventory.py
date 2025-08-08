from datetime import datetime
from typing import List, Optional, Dict, Any
from amazonapi.client import BaseClient
from models.amazonapi.spapi.inventory import (
    GetInventorySummariesResponse,
    Granularity,
)

class InventoryClient(BaseClient):
    """Client for the FBA Inventory API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_inventory_summaries(
        self, details: bool, granularity_type: str, granularity_id: str, start_date_time: datetime, seller_skus: List[str], next_token: Optional[str] = None, marketplace_ids: Optional[List[str]] = None
    ) -> GetInventorySummariesResponse:
        params = {
            "details": details,
            "granularityType": granularity_type,
            "granularityId": granularity_id,
            "startDateTime": start_date_time.isoformat(),
            "sellerSkus": ",".join(seller_skus),
        }
        if next_token:
            params["nextToken"] = next_token
        if marketplace_ids:
            params["marketplaceIds"] = ",".join(marketplace_ids)
        return await self._request(
            method="GET",
            path="/fba/inventory/v1/summaries",
            operation="getInventorySummaries",
            params=params,
            response_model=GetInventorySummariesResponse,
        ) 