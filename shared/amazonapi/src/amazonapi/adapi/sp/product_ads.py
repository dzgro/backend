from typing import List, Optional
from amazonapi.client import BaseClient
from models.amazonapi.adapi.sp.product_ads import (
    SponsoredProductsListSponsoredProductsProductAdsRequestContent,
    SponsoredProductsListSponsoredProductsProductAdsResponseContent,
    SponsoredProductsDeleteSponsoredProductsProductAdsRequestContent,
    SponsoredProductsDeleteSponsoredProductsProductAdsResponseContent,
    SponsoredProductsCreateSponsoredProductsProductAdsRequestContent,
    SponsoredProductsCreateSponsoredProductsProductAdsResponseContent,
    SponsoredProductsUpdateSponsoredProductsProductAdsRequestContent,
    SponsoredProductsUpdateSponsoredProductsProductAdsResponseContent,
)

class SPProductAdsClient(BaseClient):
    """Client for the A+ Content API."""

    async def listProductAds(
        self, request: SponsoredProductsListSponsoredProductsProductAdsRequestContent
    ) -> SponsoredProductsListSponsoredProductsProductAdsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/productAds/list",
            operation="listProductAds",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsListSponsoredProductsProductAdsResponseContent,
            headers={"Content-Type": "application/vnd.spProductAd.v3+json", "Accept": "application/vnd.spProductAd.v3+json"}
        )

    async def deleteProductAds(
        self, request: SponsoredProductsDeleteSponsoredProductsProductAdsRequestContent
    ) -> SponsoredProductsDeleteSponsoredProductsProductAdsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/productAds/delete",
            operation="deleteProductAds",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsDeleteSponsoredProductsProductAdsResponseContent,
            headers={"Content-Type": "application/vnd.spProductAd.v3+json", "Accept": "application/vnd.spProductAd.v3+json"}
        )

    async def createProductAds(
        self, request: SponsoredProductsCreateSponsoredProductsProductAdsRequestContent
    ) -> SponsoredProductsCreateSponsoredProductsProductAdsResponseContent:
        return await self._request(
            method="POST",
            path=f"/sp/productAds",
            operation="createProductAds",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsCreateSponsoredProductsProductAdsResponseContent,
            headers={"Content-Type": "application/vnd.spProductAd.v3+json", "Accept": "application/vnd.spProductAd.v3+json"}
        )
    
    async def updateProductAds(
        self, request: SponsoredProductsUpdateSponsoredProductsProductAdsRequestContent
    ) -> SponsoredProductsUpdateSponsoredProductsProductAdsResponseContent:
        return await self._request(
            method="PUT",
            path=f"/sp/productAds",
            operation="updateProductAds",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=SponsoredProductsUpdateSponsoredProductsProductAdsResponseContent,
            headers={"Content-Type": "application/vnd.spProductAd.v3+json", "Accept": "application/vnd.spProductAd.v3+json"}
        )