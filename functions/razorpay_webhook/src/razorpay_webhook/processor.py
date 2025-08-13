from razorpay_webhook.models import RazorpayWebhookPayload
from db import DbClient

class RazorpayWebhookProcessor():
    eventid: str
    verified: bool
    body:RazorpayWebhookPayload
    dbClient: DbClient
    

    def __init__(self, event: dict) -> None:
        body = event['body']
        signature = event['headers']['X-Razorpay-Signature']
        self.verified = self.verify_razorpay_signature(body, signature, 'dzgrotest')
        if not self.verified: raise ValueError("Signature verification failed")
        self.body = RazorpayWebhookPayload.model_validate_json(body)
        self.eventid = event['headers']['X-Razorpay-Event-Id']
        from dzgrosecrets import SecretManager
        self.dbClient = DbClient(SecretManager().MONGO_DB_CONNECT_URI)

    def verify_razorpay_signature(self, payload: str, received_signature: str, secret: str) -> bool:
        import hmac
        import hashlib
        generated_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(generated_signature, received_signature)

    async def execute(self):
        uid = await self.updateSubscription()
        if uid:
            await self.updatePayment(uid)

    async def updateSubscription(self):
        if self.body.subscription and self.body.subscription.notes:
            uid = self.body.subscription.notes.get('uid', None)
            if uid:
                await self.dbClient.subscriptions(uid).updateSubscriptionStatus(self.body.subscription.id, self.body.subscription.status)
                return uid

    async def updatePayment(self, uid: str):
        if self.body.payment:
            from models.collections.queue_messages import PaymentMessage
            try:
                await self.dbClient.payments(uid).getPayment(self.body.payment.id)
            except Exception as e:
                from datetime import datetime
                message = PaymentMessage(
                    index=self.body.payment.id, uid=uid,
                    amount=self.body.payment.amount / 100,
                    gst=18,
                    date= datetime.now()
                )
                from sqs import SqsHelper
                from models.sqs import SendMessageRequest
                from models.enums import QueueUrl
                req = SendMessageRequest(QueueUrl=QueueUrl.PAYMENT)
                SqsHelper(self.dbClient.sqs_messages()).sendMessage( req, message )