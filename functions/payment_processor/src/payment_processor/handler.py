import asyncio
from models.sqs import SQSEvent
from models.collections.queue_messages import PaymentMessage
from payment_processor.processor import PaymentProcessor

async def handler(event: dict, context):
    return asyncio.run(execute(SQSEvent(**event), context))


async def execute(event: SQSEvent, context):
    try:
        parsed = SQSEvent.model_validate(event)
        for record in parsed.Records:
            message = PaymentMessage.model_validate(record.dictBody)
            return await PaymentProcessor(record.messageId, message).process_message()
    except Exception as e:
        print(f"[ERROR] Failed to process message {record.messageId}: {e}")