from typing import Optional, Type, TypeVar
from dzgroshared.amazonapi.client import BaseClient
from dzgroshared.models.amazonapi.spapi.notifications import (
    CreateDestinationResponse,
    CreateDestinationRequest,
    GetDestinationsResponse,
    GetDestinationResponse,
    DeleteDestinationResponse,
    CreateSubscriptionResponse,
    CreateSubscriptionRequest,
    GetSubscriptionResponse,
    GetSubscriptionByIdResponse,
    DeleteSubscriptionByIdResponse,
)

class NotificationsClient(BaseClient):
    """Client for the Notifications API."""
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"

    async def create_destination(self, body: CreateDestinationRequest) -> CreateDestinationResponse:
        return await self._request(
            method="POST",
            path="/notifications/v1/destinations",
            operation="createDestination",
            data=body.dict(),
            response_model=CreateDestinationResponse,
        )

    async def get_destinations(self) -> GetDestinationsResponse:
        return await self._request(
            method="GET",
            path="/notifications/v1/destinations",
            operation="getDestinations",
            response_model=GetDestinationsResponse,
        )

    async def get_destination(self, destination_id: str) -> GetDestinationResponse:
        return await self._request(
            method="GET",
            path=f"/notifications/v1/destinations/{destination_id}",
            operation="getDestination",
            response_model=GetDestinationResponse,
        )

    async def delete_destination(self, destination_id: str) -> DeleteDestinationResponse:
        return await self._request(
            method="DELETE",
            path=f"/notifications/v1/destinations/{destination_id}",
            operation="deleteDestination",
            response_model=DeleteDestinationResponse,
        )

    async def create_subscription(
        self, notification_type: str, body: CreateSubscriptionRequest
    ) -> CreateSubscriptionResponse:
        return await self._request(
            method="POST",
            path=f"/notifications/v1/subscriptions/{notification_type}",
            operation="createSubscription",
            data=body.dict(),
            response_model=CreateSubscriptionResponse,
        )

    async def get_subscription(self, notification_type: str) -> GetSubscriptionResponse:
        return await self._request(
            method="GET",
            path=f"/notifications/v1/subscriptions/{notification_type}",
            operation="getSubscription",
            response_model=GetSubscriptionResponse,
        )

    async def get_subscription_by_id(self, subscription_id: str, notification_type: str) -> GetSubscriptionByIdResponse:
        return await self._request(
            method="GET",
            path=f"/notifications/v1/subscriptions/{notification_type}/{subscription_id}",
            operation="getSubscriptionById",
            response_model=GetSubscriptionByIdResponse,
        )

    async def delete_subscription_by_id(
        self, subscription_id: str, notification_type: str
    ) -> DeleteSubscriptionByIdResponse:
        return await self._request(
            method="DELETE",
            path=f"/notifications/v1/subscriptions/{notification_type}/{subscription_id}",
            operation="deleteSubscriptionById",
            response_model=DeleteSubscriptionByIdResponse,
        ) 