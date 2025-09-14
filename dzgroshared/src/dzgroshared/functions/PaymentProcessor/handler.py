from io import BytesIO
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.users.model import User
from dzgroshared.sqs.model import SQSEvent
from dzgroshared.db.queue_messages.model import PaymentMessage


class PaymentProcessor:
    client: DzgroSharedClient

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, event: dict):
        try:
            parsed = SQSEvent.model_validate(event)
            for record in parsed.Records:
                message = PaymentMessage.model_validate(record.dictBody)
                self.client.uid = message.uid
                return await self.process_message(record.messageId, message)
        except Exception as e:
            print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    async def process_message(self, messageid: str, message: PaymentMessage):
        if await self.client.db.sqs_messages.setMessageAsProcessing(messageid):
            invoiceId = await self.process_payment(message)
            buffer = await self.generateInvoice(invoiceId, message)
            self.saveToS3(buffer, invoiceId, message.uid)
            await self.client.db.sqs_messages.setMessageAsCompleted(messageid)


    async def process_payment(self, message: PaymentMessage):
        invoiceId = await self.client.db.invoice_number.getNextInvoiceId()
        await self.client.db.payments.addPayment(
            message.index,
            message.amount / 100,
            "subscription", invoiceId, message.gst
        )
        return invoiceId   

    async def generateInvoice(self, invoiceId:str, message: PaymentMessage):
        user = User(**await self.client.db.users.getUser())
        from dzgroshared.functions.PaymentProcessor.invoice import generate_gst_invoice
        return generate_gst_invoice(user, message.amount, message.gst, invoiceId, message.date)
    
    def saveToS3(self, buffer: BytesIO, invoiceId:str, uid: str):
        buffer.seek(0)
        from dzgroshared.storage.model import S3PutObjectModel, S3Bucket
        bucket = S3Bucket.INVOICES
        key = f'{uid}/invoices/{invoiceId}.pdf'
        obj = S3PutObjectModel(
            Bucket=bucket,
            Key=key,
            ContentType='application/pdf'
        )
        self.client.storage.put_object(obj, buffer.getvalue())
        return key