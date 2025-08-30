from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.collections.queue_messages import DailyReportMessage
from dzgroshared.models.enums import ENVIRONMENT, CountryCode, QueueName
from dzgroshared.models.model import LambdaContext
from dzgroshared.models.sqs import SQSEvent, SQSRecord, SendMessageRequest


async def sendMessage(client: DzgroSharedClient, event: dict, context: LambdaContext):
    try:
        country = event.get('country')
        queue = event.get('queue')
        if country and queue:
            countryCode = CountryCode(country)
            queueName = QueueName(queue)
            message = DailyReportMessage(index=countryCode)
            messageid = await client.sqs.sendMessage(
                SendMessageRequest(Queue=queue),
                MessageBody=message
            )

            if client.env==ENVIRONMENT.LOCAL:
                from dzgroshared.models.model import MockLambdaContext
                sqsEvent = SQSEvent(Records=[SQSRecord(body=message.model_dump_json(), messageId=messageid, receiptHandle='')])
                await client.functions(sqsEvent.model_dump(), context).daily_report_refresh
    except Exception as e:
        print(f"Error occurred: {e}")

