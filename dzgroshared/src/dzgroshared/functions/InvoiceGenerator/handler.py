from io import BytesIO
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.payments.model import PaymentRequest
from dzgroshared.db.queue_messages.model import GenerateInvoiceQM
from dzgroshared.db.razorpay_orders.model import RazorPayDbOrder
from dzgroshared.functions.RazorpayWebhookProcessor.models import OrderEntity, OrderPaidQM, InvoiceExpiredQM, InvoicePaidQM, PaymentEntity
from dzgroshared.sqs.model import SQSEvent, SQSRecord


class RazorpayWebhookProcessor:
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, context,  record: SQSRecord):
        self.context = context
        self.messageid = record.messageId
        message = GenerateInvoiceQM.model_validate(record.dictBody)
        self.client.setUid(message.uid)
        order = await self.client.db.razorpay_orders.getOrderById(message.orderid)
        await self.generateInvoice(order, message.paymentid)

    async def generateInvoice(self, order: RazorPayDbOrder, paymentId: str):
        if not order.paymentId:
            order.paymentId = paymentId
            await self.client.db.razorpay_orders.setOrderAsPaid(order.id, paymentId)
            invoiceId = await self.client.db.invoice_number.getNextInvoiceId()
            payment = await self.client.db.payments.addPayment(PaymentRequest(_id=invoiceId, paymentId=order.paymentId, amount=order.amount, gstrate=18))
            from dzgroshared.functions.InvoiceGenerator.invoice import generate_gst_invoice
            order = await self.client.db.razorpay_orders.getOrderById(order.id)
            gstin = await self.client.db.gstin.getGST(order.notes.gstin)
            user = await self.client.db.users.getUser()
            buffer = generate_gst_invoice(invoiceId, user, payment, gstin)
            self.saveToS3(buffer, invoiceId)
                
    def saveToS3(self, buffer: BytesIO, invoiceId:str):
        buffer.seek(0)
        from dzgroshared.storage.model import S3PutObjectModel, S3Bucket
        bucket = S3Bucket.INVOICES
        key = f'{self.client.uid}/invoices/{invoiceId}.pdf'
        obj = S3PutObjectModel(
            Bucket=bucket,
            Key=key,
            ContentType='application/pdf'
        )
        self.client.storage.put_object(obj, buffer.getvalue())
        return key