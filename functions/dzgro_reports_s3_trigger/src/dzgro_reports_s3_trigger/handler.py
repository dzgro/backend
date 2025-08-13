import asyncio
from dzgro_reports_s3_trigger.processor import DzgroReportS3TriggerProcessor

async def handler(event: dict, context):
    return asyncio.run(execute(event, context))


async def execute(event: dict, context):
    records = event.get('Records',[])
    for record in records:
        await DzgroReportS3TriggerProcessor(record).execute()