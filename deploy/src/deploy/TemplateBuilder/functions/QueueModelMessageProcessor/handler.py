import os, asyncio

from dzgroshared.db.queue_messages.model import QueueMessageModelType
client=None

def getClient():
    global client
    from dzgroshared.db.enums import ENVIRONMENT
    ENV = ENVIRONMENT(os.environ.get("ENV"))
    from dzgroshared.client import DzgroSharedClient
    client = DzgroSharedClient(ENV)
    return client


def handler(event: dict, context):
    print(event)
    asyncio.run(execute(event, context))
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }

async def execute(event: dict, context):
    from dzgroshared.sqs.model import SQSEvent
    client = getClient()
    try:
        parsed = SQSEvent.model_validate(event)
        for record in parsed.Records:
            try:
                if record.model==QueueMessageModelType.COUNTRY_REPORT:
                    await client.functions(event, context).daily_report_refresh
                elif record.model==QueueMessageModelType.DZGRO_REPORT:
                    await client.functions(event, context).dzgro_reports
                elif record.model==QueueMessageModelType.AMAZON_DAILY_REPORT:
                    await client.functions(event, context).amazon_daily_report
                elif record.model==QueueMessageModelType.ORDER_PAID:
                    await client.functions(event, context).razorpay_webhook_processor
                elif record.model==QueueMessageModelType.INVOICE_PAID:
                    await client.functions(event, context).razorpay_webhook_processor
                elif record.model==QueueMessageModelType.INVOICE_EXPIRED:
                    await client.functions(event, context).razorpay_webhook_processor
            except Exception as e:
                await client.db.sqs_messages.setMessageAsFailed(record.messageId, str(e))
    except Exception as e:
        print(f"Error occurred: {e}")
        pass