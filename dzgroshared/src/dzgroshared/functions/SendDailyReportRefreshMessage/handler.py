from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.queue_messages.model import DailyReportByCountryQM
from dzgroshared.db.enums import ENVIRONMENT, CountryCode
from dzgroshared.db.model import LambdaContext
from dzgroshared.sqs.model import QueueName, SendMessageRequest


async def sendMessage(client: DzgroSharedClient, event: dict, context: LambdaContext):
    try:
        country = event.get('country')
        queue = event.get('queue')
        if country and queue:
            countryCode = CountryCode(country)
            queueName = QueueName(queue)
            message = DailyReportByCountryQM(index=countryCode)
            messageid = await client.sqs.sendMessage(
                SendMessageRequest(Queue=queueName),
                MessageBody=message
            )
            if client.secrets.ENV==ENVIRONMENT.DEV:
                sqsEvent = client.sqs.mockSQSEvent(messageid, message.model_dump_json())
                await client.functions(sqsEvent, context).daily_report_refresh
    except Exception as e:
        print(f"Error occurred: {e}")

