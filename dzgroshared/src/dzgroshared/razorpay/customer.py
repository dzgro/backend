from typing import Any, Dict, Optional
import httpx
from dzgroshared.razorpay.error import razorpay_error_wrapper
from dzgroshared.models.razorpay.customer import CreateCustomer, Customer

class RazorpayCustomerHelper:

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.base_url = "https://api.razorpay.com/v1"

    @razorpay_error_wrapper
    async def create_customer(self, data: CreateCustomer) -> Customer:
        response = await self.client.post(f"{self.base_url}/customers", json=data.model_dump(exclude_none=True))
        response.raise_for_status()
        return Customer(**response.json())

    @razorpay_error_wrapper
    async def fetch_customer(self, customer_id: str) -> Customer:
        response = await self.client.get(f"{self.base_url}/customers/{customer_id}")
        response.raise_for_status()
        return Customer(**response.json())

    @razorpay_error_wrapper
    async def update_customer(self, customer_id: str, data: Dict[str, Any]) -> Customer:
        response = await self.client.patch(f"{self.base_url}/customers/{customer_id}", json=data)
        response.raise_for_status()
        return Customer(**response.json())

    @razorpay_error_wrapper
    async def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        response = await self.client.delete(f"{self.base_url}/customers/{customer_id}")
        response.raise_for_status()
        return response.json()

    @razorpay_error_wrapper
    async def fetch_all_customers(self, params: Optional[Dict[str, Any]] = None) -> list[Customer]:
        response = await self.client.get(f"{self.base_url}/customers", params=params)
        response.raise_for_status()
        return [Customer(**item) for item in response.json().get("items", [])]