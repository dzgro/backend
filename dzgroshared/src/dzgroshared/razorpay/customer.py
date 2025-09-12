from typing import Any, Dict, Optional
from dzgroshared.razorpay.error import razorpay_error_wrapper
from dzgroshared.models.razorpay.customer import RazorpayCreateCustomer, RazorpayCustomer
from httpx import AsyncClient

class RazorpayCustomerHelper:
    base_url: str
    client: AsyncClient

    def __init__(self, base_url: str, client: AsyncClient) -> None:
        self.base_url = base_url
        self.client = client

    @razorpay_error_wrapper
    async def create_customer(self, data: RazorpayCreateCustomer) -> RazorpayCustomer:
        response = await self.client.post(f"{self.base_url}/customers", json=data.model_dump(exclude_none=True))
        response.raise_for_status()
        return RazorpayCustomer(**response.json())

    @razorpay_error_wrapper
    async def fetch_customer(self, customer_id: str) -> RazorpayCustomer:
        response = await self.client.get(f"{self.base_url}/customers/{customer_id}")
        response.raise_for_status()
        return RazorpayCustomer(**response.json())

    @razorpay_error_wrapper
    async def update_customer(self, customer_id: str, data: Dict[str, Any]) -> RazorpayCustomer:
        response = await self.client.patch(f"{self.base_url}/customers/{customer_id}", json=data)
        response.raise_for_status()
        return RazorpayCustomer(**response.json())

    @razorpay_error_wrapper
    async def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        response = await self.client.delete(f"{self.base_url}/customers/{customer_id}")
        response.raise_for_status()
        return response.json()

    @razorpay_error_wrapper
    async def fetch_all_customers(self, params: Optional[Dict[str, Any]] = None) -> list[RazorpayCustomer]:
        response = await self.client.get(f"{self.base_url}/customers", params=params)
        response.raise_for_status()
        return [RazorpayCustomer(**item) for item in response.json().get("items", [])]