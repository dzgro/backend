from io import BytesIO
from models.collections.queue_messages import PaymentMessage
from db import DbClient

class PaymentProcessor:
    messageid: str
    message: PaymentMessage
    dbClient: DbClient

    def __init__(self, messageid: str, message: PaymentMessage) -> None:
        self.messageid = messageid
        self.message = message
        from dzgrosecrets import SecretManager
        self.dbClient = DbClient(SecretManager().MONGO_DB_CONNECT_URI)

    async def process_message(self):
        count, id = await self.dbClient.sqs_messages().setMessageAsProcessing(self.messageid)
        if count>0:
            invoiceId = await self.process_payment()
            buffer = await self.generateInvoice(invoiceId)
            self.saveToS3(buffer, invoiceId)
            await self.dbClient.sqs_messages().setMessageAsCompleted(self.messageid)


    async def process_payment(self):
        payments = self.dbClient.payments(self.message.uid)
        invoiceId = await self.dbClient.defaults().getNextInvoiceId()
        await payments.addPayment(
            self.message.index,
            self.message.amount / 100,
            "subscription", invoiceId, self.message.gst
        )
        return invoiceId   

    async def generateInvoice(self, invoiceId:str):
        from models.collections.user import User
        user = User(**await self.dbClient.user(self.message.uid).getUser())
        from payment_processor.invoice import generate_gst_invoice
        return generate_gst_invoice(user, self.message.amount, self.message.gst, invoiceId, self.message.date)
    
    def saveToS3(self, buffer: BytesIO, invoiceId:str):
        buffer.seek(0)
        from storage import S3Storage, S3Bucket
        s3 = S3Storage()
        from models.s3 import S3PutObjectModel
        bucket = S3Bucket.INVOICES
        key = f'{self.message.uid}/invoices/{invoiceId}.pdf'
        obj = S3PutObjectModel(
            Bucket=bucket,
            Key=key,
            Body=buffer.getvalue(),
            ContentType='application/pdf'
        )
        s3.put_object(obj)
        return key
