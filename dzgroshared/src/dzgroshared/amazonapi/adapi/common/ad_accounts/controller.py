from typing import List, Optional
from dzgroshared.amazonapi.client import BaseClient
from .model import AdsAccountsListResponse, AdsAccountsListRequest

class AdsAccountsClient(BaseClient):
    """Client for the Ads Account API."""

    async def listAccounts(
        self, request: AdsAccountsListRequest = AdsAccountsListRequest()
    ) -> AdsAccountsListResponse:
        return await self._request(
            method="POST",
            path=f"/adsAccounts/list",
            operation="listAdsAccounts",
            data=request.model_dump(exclude_none=True, by_alias=True),
            response_model=AdsAccountsListResponse,
            headers={"Content-Type": "application/vnd.listaccountsresource.v1+json", "Accept": "application/vnd.listaccountsresource.v1+json"}
        )
