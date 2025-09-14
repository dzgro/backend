from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from .model import ProductMetadataListResponse, ProductMetadataRequest

class ProductsMetadataClient(BaseClient):
    """Client for the Products Metadata API."""

    async def listProducts(
        self, request: ProductMetadataRequest
    ) -> ProductMetadataListResponse:
        return await self._request(
            method="POST",
            path=f"/product/metadata",
            operation="listProducts",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=ProductMetadataListResponse,
            headers={"Content-Type": "application/vnd.productmetadatarequest.v1+json", "Accept": "application/vnd.productmetadatarequest.v1+json"}
        )
