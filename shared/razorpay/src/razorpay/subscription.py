from typing import Any, Dict, Optional
import httpx
from razorpay.error import razorpay_error_wrapper
from razorpay.models.subscription import CreateSubscription, UpdateSubscription, Subscription

class RazorpaySubscriptionHelper:

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.base_url = "https://api.razorpay.com/v1"

    @razorpay_error_wrapper
    async def create_subscription(self, data: CreateSubscription) -> Subscription:
        response = await self.client.post(f"{self.base_url}/subscriptions", json=data.model_dump(exclude_none=True))
        response.raise_for_status()
        return Subscription(**response.json())

    @razorpay_error_wrapper
    async def fetch_subscription(self, subscription_id: str) -> Subscription:
        response = await self.client.get(f"{self.base_url}/subscriptions/{subscription_id}")
        response.raise_for_status()
        return Subscription(**response.json())
    
    @razorpay_error_wrapper
    async def cancel_subscription(self, subscription_id: str, data: Optional[Dict[str, Any]] = None) -> Subscription:
        response = await self.client.post(f"{self.base_url}/subscriptions/{subscription_id}/cancel", json=data or {})
        response.raise_for_status()
        return Subscription(**response.json())

    @razorpay_error_wrapper
    async def pause_subscription(self, subscription_id: str, data: Dict[str, Any]) -> Subscription:
        response = await self.client.post(f"{self.base_url}/subscriptions/{subscription_id}/pause", json=data)
        response.raise_for_status()
        return Subscription(**response.json())

    @razorpay_error_wrapper
    async def resume_subscription(self, subscription_id: str, data: Dict[str, Any]) -> Subscription:
        response = await self.client.post(f"{self.base_url}/subscriptions/{subscription_id}/resume", json=data)
        response.raise_for_status()
        return Subscription(**response.json())

    @razorpay_error_wrapper
    async def update_subscription(self, subscription_id: str, data: UpdateSubscription) -> Subscription:
        response = await self.client.patch(f"{self.base_url}/subscriptions/{subscription_id}", json=data.model_dump(exclude_none=True))
        response.raise_for_status()
        return Subscription(**response.json())

    @razorpay_error_wrapper
    async def fetch_all_subscriptions(self, params: Optional[Dict[str, Any]] = None) -> list[Subscription]:
        response = await self.client.get(f"{self.base_url}/subscriptions", params=params)
        response.raise_for_status()
        return [Subscription(**item) for item in response.json().get("items", [])]