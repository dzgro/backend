from typing import List, Optional, Dict, Any
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.spapi.listings import (
    GetListingsItemResponse,ItemSearchResults
)
from datetime import datetime
from typing import Literal


class ListingsClient(BaseClient):
    """Client for the Listings API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_listings_item(
        self, seller_id: str, sku: str, issue_locale: Optional[str] = None, included_data: Optional[List[str]] = None
    ) -> GetListingsItemResponse:
        params = {"marketplaceIds": ",".join(self.config.marketplaceid)}
        if issue_locale:
            params["issueLocale"] = issue_locale
        if included_data:
            params["includedData"] = ",".join(included_data)
        return await self._request(
            method="GET",
            path=f"/listings/2021-08-01/items/{seller_id}/{sku}",
            operation="getListingsItem",
            params=params,
            response_model=GetListingsItemResponse,
        ) 
    
    async def search_listings_items(
        self, 
        seller_id: str, 
        included_data: List[str], 
        lastUpdatedAfter: Optional[datetime] = None,
        sortBy: Optional[Literal['lastUpdatedDate','sku','createdDate']] = None,
        sortOrder: Optional[Literal['ASC','DESC']] = None,
        pageSize: int = 20,
        pageToken: Optional[str|None] = None
    ) -> ItemSearchResults:
        params: dict = {"marketplaceIds": self.config.marketplaceid}
        if lastUpdatedAfter:
            params["lastUpdatedAfter"] = lastUpdatedAfter.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if included_data:
            params["includedData"] = ",".join(included_data)
        if sortBy:
            params["sortBy"] = sortBy
        if sortOrder:
            params["sortOrder"] = sortOrder
        params["pageSize"] = pageSize
        if pageToken:
            params["pageToken"] = pageToken
        return await self._request(
            method="GET",
            path=f"/listings/2021-08-01/items/{seller_id}",
            operation="searchListingsItem",
            params=params,
            response_model=ItemSearchResults,
        ) 