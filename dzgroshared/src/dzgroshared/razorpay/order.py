from dzgroshared.razorpay.error import razorpay_error_wrapper
from dzgroshared.models.razorpay.order import RazorpayCreateOrder, RazorpayOrder
from httpx import AsyncClient


class RazorpayOrderHelper:
    base_url: str
    client: AsyncClient

    def __init__(self, base_url: str, client: AsyncClient) -> None:
        self.base_url = base_url
        self.client = client

    @razorpay_error_wrapper
    async def create_order(self, data: RazorpayCreateOrder) -> RazorpayOrder:
        response = await self.client.post(f"{self.base_url}/orders", json=data.model_dump(exclude_none=True))
        response.raise_for_status()
        return RazorpayOrder.model_validate(response.json())
