import asyncio
from razorpay_webhook.processor import RazorpayWebhookProcessor

async def handler(event: dict, context):
    return asyncio.run(execute(event, context))


async def execute(event: dict, context):
    records = event.get('Records',[])
    for record in records:
        try:    
            await RazorpayWebhookProcessor(record).execute()
        except Exception as e:
            pass