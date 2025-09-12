from fastapi import APIRouter, Request
from api.Util import RequestHelper
from dzgroshared.models.collections.payments import PaymentStatus, PaymentList, Payment
from dzgroshared.models.model import Paginator
router = APIRouter(prefix="/payments", tags=["Payments"])

async def client(request: Request):
    return (await RequestHelper(request).client)

async def db(request: Request):
    return (await client(request)).db.payments

@router.post("/", response_model=PaymentList, response_model_exclude_none=True, response_model_by_alias=False)
async def getPayments(request: Request, paginator: Paginator):
    return (await db(request)).getPayments(paginator)

@router.get("/payment-link/{id}", response_model=Payment, response_model_exclude_none=True, response_model_by_alias=False)
async def generateInvoiceLink(request: Request, id: str):
    _client = await client(request)
    _payments = (await db(request))
    payment = await _payments.getPayment(id)
    if payment.status in [PaymentStatus.GENERATING_INVOICE, PaymentStatus.INVOICE_GENERATION_FAILED]: raise ValueError("Invoice is being generated.")
    elif payment.status == PaymentStatus.CAPTURED: raise ValueError("Invoice will be generated soon. Please try after some time.")
    path = f'{_client.uid}/invoices/INV-{payment.invoice}.pdf'
    from dzgroshared.storage.client import S3Storage
    from dzgroshared.models.s3 import S3Bucket
    payment.invoicelink = S3Storage(_client).create_signed_url_by_path(path, bucket=S3Bucket.INVOICES)
    return payment
