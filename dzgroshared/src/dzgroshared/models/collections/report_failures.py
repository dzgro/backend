
from datetime import datetime
from dzgroshared.models.model import MarketplaceObjectId
from dzgroshared.models.sqs import SQSBatchFailedMessage
from pydantic import BaseModel

class DailyReportFailure(MarketplaceObjectId):
    message: SQSBatchFailedMessage
    createdat: datetime