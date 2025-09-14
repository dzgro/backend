from dzgroshared.razorpay.error import razorpay_error_wrapper
from dzgroshared.razorpay.invoice.model import RazorpayCreateInvoice, RazorpayInvoice
from httpx import AsyncClient

class RazorpayInvoiceHelper:
    base_url: str
    client: AsyncClient

    def __init__(self, base_url: str, client: AsyncClient) -> None:
        self.base_url = base_url
        self.client = client

    @razorpay_error_wrapper
    async def create_invoice(self, data: RazorpayCreateInvoice) -> RazorpayInvoice:
        response = await self.client.post(f"{self.base_url}/invoices", json=data.model_dump(exclude_none=True))
        response.raise_for_status()
        return RazorpayInvoice.model_validate(response.json())

    @razorpay_error_wrapper
    async def get_invoice(self, id: str) -> RazorpayInvoice:
        response = await self.client.get(f"{self.base_url}/invoices/{id}")
        response.raise_for_status()
        return RazorpayInvoice.model_validate(response.json())

    @razorpay_error_wrapper
    async def issue_invoice(self, id: str) -> RazorpayInvoice:
        invoice = await self.get_invoice(id)
        if invoice.status != 'draft': raise ValueError("Only draft invoices can be issued.")
        response = await self.client.post(f"{self.base_url}/invoices/{id}/issue")
        response.raise_for_status()
        invoice = RazorpayInvoice.model_validate(response.json())
        if invoice.status != 'issued': raise ValueError("Invoice status is not 'issued' after issuing.")
        return invoice
