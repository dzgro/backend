from dzgroshared.amazonapi.client import BaseClient
from .model import GetMarketplaceParticipationsResponse

class SellersClient(BaseClient):
    """Client for the Sellers API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_marketplace_participations(self) -> GetMarketplaceParticipationsResponse:
        return await self._request(
            method="GET",
            path="/sellers/v1/marketplaceParticipations",
            operation="getMarketplaceParticipations",
            response_model=GetMarketplaceParticipationsResponse,
        ) 