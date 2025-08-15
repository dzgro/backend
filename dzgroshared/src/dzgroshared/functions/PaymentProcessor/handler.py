from io import BytesIO
from dzgroshared.functions import FunctionClient
from dzgroshared.models.collections.user import User
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.models.collections.queue_messages import PaymentMessage


class PaymentProcessor:
    fnclient: FunctionClient

    def __init__(self, client: FunctionClient):
        self.fnclient = client

    async def execute(self):
        try:
            parsed = SQSEvent.model_validate(self.fnclient.event)
            for record in parsed.Records:
                message = PaymentMessage.model_validate(record.dictBody)
                self.fnclient.client.uid = message.uid
                return await self.process_message(record.messageId, message)
        except Exception as e:
            print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    async def process_message(self, messageid: str, message: PaymentMessage):
        count, id = await self.fnclient.client.db.sqs_messages.setMessageAsProcessing(messageid)
        if count > 0:
            invoiceId = await self.process_payment(message)
            buffer = await self.generateInvoice(invoiceId, message)
            self.saveToS3(buffer, invoiceId, message.uid)
            await self.fnclient.client.db.sqs_messages.setMessageAsCompleted(messageid)


    async def process_payment(self, message: PaymentMessage):
        invoiceId = await self.fnclient.client.db.defaults.getNextInvoiceId()
        await self.fnclient.client.db.payments.addPayment(
            message.index,
            message.amount / 100,
            "subscription", invoiceId, message.gst
        )
        return invoiceId   

    async def generateInvoice(self, invoiceId:str, message: PaymentMessage):
        user = User(**await self.fnclient.client.db.user.getUser())
        from dzgroshared.functions.PaymentProcessor.invoice import generate_gst_invoice
        return generate_gst_invoice(user, message.amount, message.gst, invoiceId, message.date)
    
    def saveToS3(self, buffer: BytesIO, invoiceId:str, uid: str):
        buffer.seek(0)
        from dzgroshared.models.s3 import S3PutObjectModel, S3Bucket
        bucket = S3Bucket.INVOICES
        key = f'{uid}/invoices/{invoiceId}.pdf'
        obj = S3PutObjectModel(
            Bucket=bucket,
            Key=key,
            Body=buffer.getvalue(),
            ContentType='application/pdf'
        )
        self.fnclient.client.storage.put_object(obj)
        return key