from typing import Any, Dict, Optional
from dzgroshared.razorpay.error import razorpay_error_wrapper
from dzgroshared.razorpay.customer.model import RazorpayCreateCustomer, RazorpayCustomer
from httpx import AsyncClient

class RazorpayAddOnHelper:
    base_url: str
    client: AsyncClient

    def __init__(self, base_url: str, client: AsyncClient) -> None:
        self.base_url = base_url
        self.client = client
