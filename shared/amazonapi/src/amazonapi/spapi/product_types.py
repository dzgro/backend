from typing import List, Optional
from amazonapi.client import BaseClient
from models.amazonapi.spapi.product_types import ProductTypeList, Requirements, RequirementsEnforced, GetDefinitionsProductTypeResponse

class ProductTypesClient(BaseClient):
    """Client for the Product Type Definitions API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def search_definitions_product_types(
        self, marketplace_ids: List[str], keywords: Optional[List[str]] = None
    ) -> ProductTypeList:
        params = {"marketplaceIds": ",".join(marketplace_ids)}
        if keywords:
            params["keywords"] = ",".join(keywords)
        return await self._request(
            method="GET",
            path="/definitions/2020-09-01/productTypes",
            operation="searchDefinitionsProductTypes",
            params=params,
            response_model=ProductTypeList,
        )

    async def get_definitions_product_type(
        self, product_type: str, marketplace_ids: List[str], seller_id: Optional[str] = None, product_type_version: Optional[str] = None, requirements: Optional[str] = None, requirements_enforced: Optional[str] = None, locale: Optional[str] = None
    ) -> GetDefinitionsProductTypeResponse:
        params = {"marketplaceIds": ",".join(marketplace_ids)}
        if seller_id:
            params["sellerId"] = seller_id
        if product_type_version:
            params["productTypeVersion"] = product_type_version
        if requirements:
            params["requirements"] = requirements
        if requirements_enforced:
            params["requirementsEnforced"] = requirements_enforced
        if locale:
            params["locale"] = locale
        return await self._request(
            method="GET",
            path=f"/definitions/2020-09-01/productTypes/{product_type}",
            operation="getDefinitionsProductType",
            params=params,
            response_model=GetDefinitionsProductTypeResponse,
        ) 