from typing import List
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.spapi.solicitations import GetSolicitationActionsForOrderResponse, CreateProductReviewAndSellerFeedbackSolicitationResponse

class SolicitationsClient(BaseClient):
    """Client for the Solicitations API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def get_solicitation_actions_for_order(
        self, amazon_order_id: str, marketplace_ids: List[str]
    ) -> GetSolicitationActionsForOrderResponse:
        params = {"marketplaceIds": ",".join(marketplace_ids)}
        return await self._request(
            method="GET",
            path=f"/solicitations/v1/orders/{amazon_order_id}",
            operation="getSolicitationActionsForOrder",
            params=params,
            response_model=GetSolicitationActionsForOrderResponse,
        )

    async def create_product_review_and_seller_feedback_solicitation(
        self, amazon_order_id: str, marketplace_ids: List[str]
    ) -> CreateProductReviewAndSellerFeedbackSolicitationResponse:
        params = {"marketplaceIds": ",".join(marketplace_ids)}
        return await self._request(
            method="POST",
            path=f"/solicitations/v1/orders/{amazon_order_id}/solicitations/productReviewAndSellerFeedback",
            operation="createProductReviewAndSellerFeedbackSolicitation",
            params=params,
            response_model=CreateProductReviewAndSellerFeedbackSolicitationResponse,
        ) 