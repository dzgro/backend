from io import BytesIO
from dzgroshared.functions import FunctionClient
from dzgroshared.functions.RazorpayWebhookProcessor.models import RazorpayWebhookPayload
from dzgroshared.models.collections.user import User
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.models.collections.queue_messages import PaymentMessage


class RazorpayWebhookProcessor:
    fnclient: FunctionClient

    def __init__(self, client: FunctionClient):
        self.fnclient = client

    async def execute(self):
        records = self.fnclient.event.get('Records',[])
        for record in records:
            try:
                parsed = SQSEvent.model_validate(self.fnclient.event)
                for record in parsed.Records:
                    if record.messageAttributes:
                        if 'X-Razorpay-Signature' in record.messageAttributes and 'X-Razorpay-Event-Id' in record.messageAttributes:
                            signature = record.messageAttributes['X-Razorpay-Signature'].stringValue
                            if not signature: raise ValueError("Missing Razorpay signature")
                            event_id = record.messageAttributes['X-Razorpay-Event-Id'].stringValue
                            if not event_id: raise ValueError("Missing Razorpay event ID")
                            self.verified = self.verify_razorpay_signature(record.body, signature, 'dzgrotest')
                            if not self.verified: raise ValueError("Signature verification failed")
                            message = RazorpayWebhookPayload.model_validate(record.dictBody)
                            await self.processMessage(message)
            except Exception as e:
                print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    def verify_razorpay_signature(self, payload: str, received_signature: str, secret: str) -> bool:
        import hmac
        import hashlib
        generated_signature = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(generated_signature, received_signature)
    
    async def processMessage(self, message: RazorpayWebhookPayload):
        uid = await self.updateSubscription(message)
        if uid:
            await self.updatePayment(uid, message)

    async def updateSubscription(self, body: RazorpayWebhookPayload):
        if body.subscription and body.subscription.notes:
            uid = body.subscription.notes.get('uid', None)
            if uid:
                self.fnclient.client.uid = uid
                await self.fnclient.client.db.subscriptions.updateSubscriptionStatus(body.subscription.id, body.subscription.status)
                return uid

    async def updatePayment(self, uid: str, body: RazorpayWebhookPayload):
        if body.payment:
            try:
                await self.fnclient.client.db.payments.getPayment(body.payment.id)
            except Exception as e:
                from datetime import datetime
                from dzgroshared.models.collections.queue_messages import PaymentMessage
                message = PaymentMessage(
                    index=body.payment.id, uid=uid,
                    amount=body.payment.amount / 100,
                    gst=18,
                    date= datetime.now()
                )
                from dzgroshared.models.enums import QueueUrl
                from dzgroshared.models.sqs import SendMessageRequest
                req = SendMessageRequest(QueueUrl=QueueUrl.PAYMENT)
                self.fnclient.client.sqs.sendMessage(req, message)