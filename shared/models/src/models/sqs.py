from pydantic import BaseModel, model_validator, Field, computed_field, ConfigDict, conint
from pydantic.json_schema import SkipJsonSchema
from typing import Optional, Dict
from enum import Enum
from typing import Optional, Dict, List, Any
from enum import Enum
import json
from datetime import datetime
from models.enums import QueueUrl

# ================================
# 📥 RECEIVING FROM SQS (Lambda Input)
# ================================
class SQSAttributes(BaseModel):
    model_config = ConfigDict(extra="allow")  # allow unexpected attributes
    ApproximateReceiveCount: int
    SentTimestamp: datetime
    SenderId: str
    ApproximateFirstReceiveTimestamp: datetime
    MessageDeduplicationId: str|SkipJsonSchema[None] = None  # FIFO only
    MessageGroupId: str|SkipJsonSchema[None] = None          # FIFO only
    SequenceNumber: int|SkipJsonSchema[None] = None          # FIFO only

    @model_validator(mode="before")
    @classmethod
    def parse_timestamps(cls, data: dict) -> dict:
        if "SentTimestamp" in data:
            data["SentTimestamp"] = datetime.fromtimestamp(int(data["SentTimestamp"]) / 1000)
        if "ApproximateFirstReceiveTimestamp" in data:
            data["ApproximateFirstReceiveTimestamp"] = datetime.fromtimestamp(
                int(data["ApproximateFirstReceiveTimestamp"]) / 1000
            )
        if "ApproximateReceiveCount" in data:
            data["ApproximateReceiveCount"] = int(data["ApproximateReceiveCount"])
        if "SequenceNumber" in data:
            try:
                data["SequenceNumber"] = int(data["SequenceNumber"])
            except ValueError:
                pass  # fallback to str if conversion fails
        return data

class SQSMessageAttribute(BaseModel):
    stringValue: str|SkipJsonSchema[None] = None
    binaryValue: str | SkipJsonSchema[None] = None
    stringListValues: List[str] = Field(default_factory=list)
    binaryListValues: List[str] = Field(default_factory=list)
    dataType: str


class SQSRecord(BaseModel):
    messageId: str
    receiptHandle: str
    body: str
    attributes: SQSAttributes | SkipJsonSchema[None] = None
    messageAttributes: Dict[str, SQSMessageAttribute] | SkipJsonSchema[None] = None
    md5OfBody: str | SkipJsonSchema[None] = None
    eventSource: str
    eventSourceARN: str
    awsRegion: str
    md5OfMessageAttributes: str | SkipJsonSchema[None] = None

    def _safe_json_parse(self) -> Any:
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return self.body.strip()

    @computed_field
    @property
    def flat_message_attributes(self) -> Dict[str, str]:
        if not self.messageAttributes:
            return {}
        result = {}
        for key, attr in self.messageAttributes.items():
            val = attr.stringValue or attr.binaryValue
            if val is not None:
                result[key] = val
        return result
    
    @computed_field
    @property
    def parsed_body(self) -> Any:
        value = self._safe_json_parse()
        val_str = str(value).strip().lower()
        if val_str in {"true", "false", "null"}:
            return {"true": True, "false": False, "null": None}[val_str]
        try:
            if isinstance(value, str) and "." in value:
                return float(value)
            return int(value)
        except (ValueError, TypeError):
            return value

    @computed_field
    @property
    def dictBody(self) -> Optional[Dict[str, Any]]:
        return self.parsed_body if isinstance(self.parsed_body, dict) else None

    @computed_field
    @property
    def listBody(self) -> Optional[List[Any]]:
        return self.parsed_body if isinstance(self.parsed_body, list) else None

    @computed_field
    @property
    def intBody(self) -> Optional[int]:
        return self.parsed_body if isinstance(self.parsed_body, int) else None

    @computed_field
    @property
    def floatBody(self) -> Optional[float]:
        return self.parsed_body if isinstance(self.parsed_body, float) else None

    @computed_field
    @property
    def strBody(self) -> Optional[str]:
        return self.parsed_body if isinstance(self.parsed_body, str) else None

    @computed_field
    @property
    def boolBody(self) -> Optional[bool]:
        return self.parsed_body if isinstance(self.parsed_body, bool) else None


class SQSEvent(BaseModel):
    Records: List[SQSRecord]


# ================================
# 📤 SENDING TO SQS
# ================================

class MessageAttributeDataType(str, Enum):
    string = "String"
    number = "Number"
    binary = "Binary"


class SendMessageAttribute(BaseModel):
    DataType: MessageAttributeDataType
    StringValue: str | SkipJsonSchema[None] = None
    BinaryValue: bytes | SkipJsonSchema[None] = None

    @model_validator(mode="after")
    def validate_content_by_datatype(self) -> "SendMessageAttribute":
        if self.DataType in {"String", "Number"}:
            if self.StringValue is None:
                raise ValueError(f"{self.DataType} requires 'StringValue'")
        elif self.DataType == "Binary":
            if self.BinaryValue is None:
                raise ValueError("Binary requires 'BinaryValue'")
        return self
class SendMessageRequest(BaseModel):
    QueueUrl: QueueUrl
    DelaySeconds: int = Field( default=0, ge=0, le=900)
    MessageAttributes: Dict[str, SendMessageAttribute] | SkipJsonSchema[None] = None

class SQSSendMessageResponse(BaseModel):
    success: bool = Field(..., description="Whether the message was sent successfully")
    message_id: str = ''
    sequence_number: str|SkipJsonSchema[None] = None
    error: Optional[str] = None

class SendMessageBatchEntry(BaseModel):
    Id: str
    MessageBody: str
    DelaySeconds: int | SkipJsonSchema[None] = None
    MessageAttributes: Dict[str, SendMessageAttribute] | SkipJsonSchema[None] = None

class SendMessageBatchRequest(BaseModel):
    QueueUrl: QueueUrl
    Entries: List[SendMessageBatchEntry]


from botocore.exceptions import BotoCoreError, ClientError
from typing import Callable, Type
from functools import wraps

def aws_error_handler():
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (BotoCoreError, ClientError) as e:
                return SQSSendMessageResponse(success=False, error=str(e))
            except Exception as e:
                return SQSSendMessageResponse(success=False, error=f"Unexpected error: {e}")
        return wrapper
    return decorator