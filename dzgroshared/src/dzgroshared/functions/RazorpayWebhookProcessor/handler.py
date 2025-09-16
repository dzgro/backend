from io import BytesIO
from bson import ObjectId
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.payments.model import PaymentRequest
from dzgroshared.functions.RazorpayWebhookProcessor.models import OrderEntity, OrderPaidBody, InvoiceExpiredBody, InvoicePaidBody, PaymentEntity
from dzgroshared.sqs.model import SQSEvent


class RazorpayWebhookProcessor:
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event: dict):
        records = event.get('Records',[])
        for record in records:
            try:
                parsed = SQSEvent.model_validate(event)
                for record in parsed.Records:
                    if record.messageAttributes:
                        if 'X-Razorpay-Signature' in record.messageAttributes and 'X-Razorpay-Event-Id' in record.messageAttributes:
                            signature = record.messageAttributes['X-Razorpay-Signature'].stringValue
                            if not signature: raise ValueError("Missing Razorpay signature")
                            event_id = record.messageAttributes['X-Razorpay-Event-Id'].stringValue
                            if not event_id: raise ValueError("Missing Razorpay event ID")
                            self.verified = self.verify_razorpay_signature(record.body, signature, self.client.secrets.RAZORPAY_WEBHOOK_SECRET)
                            if not self.verified: raise ValueError("Signature verification failed")
                            if record.dictBody: await self.processMessage(record.dictBody)
                            return True
            except Exception as e:
                print(f"[ERROR] Failed to process message {record.messageId}: {e}")
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
            obj = OrderPaidBody.model_validate(message['payload'])
            await self.updateOrder(obj)
        elif message['event']=="invoice.paid":
            obj = InvoicePaidBody.model_validate(message['payload'])
            await self.updatePaidInvoice(obj)
        elif message['event']=="invoice.expired":
            obj = InvoiceExpiredBody.model_validate(message['payload'])
            await self.updateExpiredInvoice(obj)        

    def setNotes(self, notes: dict):
        if notes:
            uid = notes.get('uid', None)
            marketplace = notes.get('marketplace', None)
            if uid: self.client.uid = uid
            if marketplace: self.client.marketplaceId = ObjectId(marketplace)

    async def updateOrder(self, order: OrderPaidBody):
        self.setNotes(order.order.notes)
        success = await self.client.db.razorpay_orders.setOrderAsPaid(order.order.id, order.payment.id)
        if success: await self.generateInvoice(order.order, order.payment)
                

    async def updatePaidInvoice(self, invoice: InvoicePaidBody):
        self.setNotes(invoice.invoice.notes)
        success = await self.client.db.razorpay_orders.setOrderAsPaid(invoice.invoice.order_id, invoice.payment.id)
        if success: await self.generateInvoice(invoice.order, invoice.payment)


    async def updateExpiredInvoice(self, invoice: InvoiceExpiredBody):
        self.setNotes(invoice.invoice.notes)
        await self.client.db.razorpay_orders.setInvoiceOrderAsExpired(invoice.invoice.order_id)

    async def generateInvoice(self, orderEntity:OrderEntity, paymentEntity: PaymentEntity):
        invoiceId = await self.client.db.invoice_number.getNextInvoiceId()
        payment = await self.client.db.payments.addPayment(PaymentRequest(_id=invoiceId, paymentId=paymentEntity.id, amount=round(paymentEntity.amount / 100,2), gstrate=18))
        from dzgroshared.functions.RazorpayWebhookProcessor.invoice import generate_gst_invoice
        order = await self.client.db.razorpay_orders.getOrderById(orderEntity.id)
        gstin = None if not order.gstin else await self.client.db.gstin.getGST(order.gstin)
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