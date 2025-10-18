from io import BytesIO
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.payments.model import PaymentRequest
from dzgroshared.functions.RazorpayWebhookProcessor.models import OrderEntity, OrderPaidQM, InvoiceExpiredQM, InvoicePaidQM, PaymentEntity
from dzgroshared.sqs.model import SQSEvent, SQSRecord


class RazorpayWebhookProcessor:
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, record: SQSRecord):
        if 'X-Razorpay-Signature' in record.messageAttributes and 'X-Razorpay-Event-Id' in record.messageAttributes:
            signature = record.messageAttributes['X-Razorpay-Signature'].stringValue
            if not signature: raise ValueError("Missing Razorpay signature")
            event_id = record.messageAttributes['X-Razorpay-Event-Id'].stringValue
            if not event_id: raise ValueError("Missing Razorpay event ID")
            self.verified = self.verify_razorpay_signature(record.body, signature, self.client.secrets.RAZORPAY_WEBHOOK_SECRET)
            if not self.verified: raise ValueError("Signature verification failed")
            if record.dictBody: await self.processMessage(record.dictBody)
            return True

    def verify_razorpay_signature(self, payload: str, received_signature: str, secret: str) -> bool:
        import hmac
        import hashlib
        generated_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(generated_signature, received_signature)
    
    async def processMessage(self, message: dict):
        if message['event']=="order.paid":
            obj = OrderPaidQM.model_validate(message['payload'])
            await self.updateOrder(obj)
        elif message['event']=="invoice.paid":
            obj = InvoicePaidQM.model_validate(message['payload'])
            await self.updatePaidInvoice(obj)
        elif message['event']=="invoice.expired":
            obj = InvoiceExpiredQM.model_validate(message['payload'])
            await self.updateExpiredInvoice(obj)        

    def setNotes(self, notes: dict):
        if notes:
            uid = notes.get('uid', None)
            if uid: self.client.uid = uid
        if not self.client.uid: raise ValueError("UID not found in notes")

    async def updateOrder(self, order: OrderPaidQM):
        self.setNotes(order.order.notes)
        success = await self.client.db.razorpay_orders.setOrderAsPaid(order.order.id, order.payment.id)
        if success: await self.generateInvoice(order.order, order.payment)
                

    async def updatePaidInvoice(self, invoice: InvoicePaidQM):
        self.setNotes(invoice.invoice.notes)
        success = await self.client.db.razorpay_orders.setOrderAsPaid(invoice.invoice.order_id, invoice.payment.id)
        if success: await self.generateInvoice(invoice.order, invoice.payment)


    async def updateExpiredInvoice(self, invoice: InvoiceExpiredQM):
        self.setNotes(invoice.invoice.notes)
        await self.client.db.razorpay_orders.setInvoiceOrderAsExpired(invoice.invoice.order_id)

    async def generateInvoice(self, order: OrderEntity, payment: PaymentEntity):
        from dzgroshared.sqs import utils
        await utils.sendGenerateInvoiceMessage(self.client, order.id, payment.id)
            