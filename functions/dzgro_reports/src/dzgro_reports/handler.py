from models.sqs import SQSEvent
from models.collections.queue_messages import DzgroReportQueueMessage
import asyncio

async def handler(event: dict, context):
    return asyncio.run(execute(SQSEvent(**event), context))


async def execute(event: SQSEvent, context):
    try:
        parsed = SQSEvent.model_validate(event)
        for record in parsed.Records:
            message = DzgroReportQueueMessage.model_validate(record.dictBody)
            from dzgro_reports.processor import DzgroReportProcessor
            return await DzgroReportProcessor(record.messageId, message).processReport()
    except Exception as e:
        print(f"[ERROR] Failed to process message {record.messageId}: {e}")
        

