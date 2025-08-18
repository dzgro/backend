from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.models.collections.payments import Payments, Payment
from dzgroshared.models.model import Paginator
router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/", response_model=Payments, response_model_exclude_none=True, response_model_by_alias=False)
async def getPayments(request: Request, paginator: Paginator):
    return await RequestHelper(request).client.db.payments.getPayments(paginator)

@router.get("/payment-link/{id}", response_model=Payment, response_model_exclude_none=True, response_model_by_alias=False)
async def generateInvoiceLink(request: Request, id: str):
    _payments = RequestHelper(request).client.db.payments
    payment = Payment(**await _payments.getPayment(id))
    if not payment.invoice: raise ValueError("Invoice is being generated.")
    path = f'{_payments.uid}/invoices/INV-{payment.invoice}.pdf'
    from dzgroshared.storage.client import S3Storage
    from dzgroshared.models.s3 import S3Bucket
    payment.invoicelink = S3Storage().create_signed_url_by_path(path, bucket=S3Bucket.INVOICES)
    return payment
