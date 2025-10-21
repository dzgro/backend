
import asyncio
from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.queue_messages.model import AmazoMarketplaceDailyReportQM, DailyReportByCountryQM
from dzgroshared.db.enums import ENVIRONMENT, AmazonDailyReportAggregationStep, CollectionType, CountryCode, MarketplaceStatus
from dzgroshared.db.model import LambdaContext
from dzgroshared.sqs.model import BatchMessageRequest, QueueName, SQSEvent, SQSRecord
from dzgroshared.sqs.utils import SQSUtils


class DailyReportRefreshByCountryCodeProcessor:
    client: DzgroSharedClient
    context: LambdaContext
    messageid: str

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    async def execute(self, context,  record: SQSRecord):
        self.context = context
        self.messageid = record.messageId
        message = DailyReportByCountryQM.model_validate(record.dictBody)
        return await SQSUtils(self.client, record, self.context).executeAmazonReportsByCountryCode(message.index)