import os, asyncio
all_vars = dict(os.environ)
client=None

def getClient():
    global client
    if client: return client
    from dzgroshared.client import DzgroSharedClient
    client = DzgroSharedClient()
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
        fn = client.functions(event, context)
        from dzgroshared.db.queue_messages.model import QueueMessageModelType
        for record in parsed.Records:
            fn.setRecord(record)
            try:
                if record.model==QueueMessageModelType.COUNTRY_REPORT:
                    await fn.daily_report_refresh
                elif record.model==QueueMessageModelType.DZGRO_REPORT:
                    await fn.dzgro_reports
                elif record.model==QueueMessageModelType.AMAZON_DAILY_REPORT:
                    await fn.amazon_daily_report
                elif record.model==QueueMessageModelType.GENERATE_INVOICE:
                    await fn.invoice_generator
                elif record.model in [QueueMessageModelType.ORDER_PAID, QueueMessageModelType.INVOICE_PAID, QueueMessageModelType.INVOICE_EXPIRED]:
                    await fn.razorpay_webhook_processor
            except Exception as e:
                await client.db.sqs_messages.setMessageAsFailed(record.messageId, str(e))
    except Exception as e:
        print(f"Error occurred: {e}")
        pass