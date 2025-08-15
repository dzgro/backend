from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.spapi.catalog import (
    GetCatalogItemResponse,
    SearchCatalogItemsResponse,
    IncludedData,
    Item, ItemSearchResults
)

class CatalogClient(BaseClient):
    """Client for the Catalog Items API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_catalog_item(
        self, asin: str, marketplace_id: str, included_data: Optional[List[IncludedData]] = None, locale: Optional[str] = None
    ) -> Item:
        params = {"marketplaceIds": marketplace_id}
        if included_data:
            params["includedData"] = ",".join([data.value for data in included_data])
        if locale:
            params["locale"] = locale
        return await self._request(
            method="GET",
            path=f"/catalog/2022-04-01/items/{asin}",
            operation="getCatalogItem",
            params=params,
            response_model=Item,
        )

    async def search_catalog_items(
        self, marketplace_id: str, keywords: List[str], included_data: Optional[List[IncludedData]] = None, brand_names: Optional[List[str]] = None, classification_ids: Optional[List[str]] = None, page_size: Optional[int] = None, page_token: Optional[str] = None, keywords_locale: Optional[str] = None, locale: Optional[str] = None
    ) -> ItemSearchResults:
        params: dict = {"marketplaceIds": marketplace_id, "keywords": ",".join(keywords)}
        if included_data:
            params["includedData"] = ",".join([data.value for data in included_data])
        if brand_names:
            params["brandNames"] = ",".join(brand_names)
        if classification_ids:
            params["classificationIds"] = ",".join(classification_ids)
        if page_size:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token
        if keywords_locale:
            params["keywordsLocale"] = keywords_locale
        if locale:
            params["locale"] = locale
        return await self._request(
            method="GET",
            path="/catalog/2022-04-01/items",
            operation="searchCatalogItems",
            params=params,
            response_model=ItemSearchResults,
        ) 