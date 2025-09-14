
from datetime import datetime
from dzgroshared.db.model import MarketplaceObjectId
from dzgroshared.sqs.model import SQSBatchFailedMessage
from pydantic import BaseModel

class DailyReportFailure(MarketplaceObjectId):
    message: SQSBatchFailedMessage
    createdat: datetime