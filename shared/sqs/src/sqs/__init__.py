
from db.collections.queue_messages import QueueMessagesHelper
from pydantic import BaseModel
import json
from sqs.model import aws_error_handler, SendMessageRequest, SQSSendMessageResponse
import uuid
from mypy_boto3_sqs import SQSClient
from db import DbClient

class SqsManager:
    client: SQSClient

    def __init__(self) -> None:
        import boto3
        from botocore.config import Config
        from typing import cast
        self.client = cast(SQSClient, boto3.client('sqs', config=Config(region_name = 'ap-south-1')))

    def __getattr__(self, item):
        return None
            

class SqsHelper(SqsManager):
    sqsDB: QueueMessagesHelper
    def __init__(self, MONGODB_URI: str) -> None:
        super().__init__()
        self.sqsDB = DbClient(MONGODB_URI).sqs_messages()

    @aws_error_handler()
    async def sendMessage(self, payload: SendMessageRequest, MessageBody: BaseModel)->SQSSendMessageResponse:
        send_args = {
            "QueueUrl": payload.QueueUrl.value,
            "MessageBody": json.dumps(MessageBody),
            "DelaySeconds": payload.DelaySeconds or 0,
        }
        if payload.MessageAttributes: send_args["MessageAttributes"] = { key: attr.model_dump(exclude_none=True) for key, attr in payload.MessageAttributes.items() }
        if self.client is None:
            raise RuntimeError("SQS client is not initialized.")
        response = self.client.send_message(**send_args)
        res = SQSSendMessageResponse(
            success=True,
            message_id=response.get("MessageId"),
            sequence_number=response.get("SequenceNumber")
        )
        await self.sqsDB.addMessageToDb(res.message_id, MessageBody)
        return res
    
    async def mockMessage(self, payload: SendMessageRequest, MessageBody: BaseModel)->SQSSendMessageResponse:
        res = SQSSendMessageResponse(
            success=True,
            message_id=str(uuid.uuid4())
        )
        await self.sqsDB.addMessageToDb(res.message_id, MessageBody)
        return res

    
    


    
    # def sendMessages(self, batch: MessageBatch):
    #     return sqs.client.send_message_batch(QueueUrl=self.queue.value, Entries=[{"Id": message.Id, "MessageBody": json.dumps(message.MessageBody), "MessageAttributes": message.MessageAttributes, "DelaySeconds": message.DelaySeconds} for message in batch.messages])

    
    # def deleteMessage(self, receiptHandle: str):
    #     sqs.client.delete_message(QueueUrl=self.queue.value, ReceiptHandle=receiptHandle)

    # def getMessages(self, MaxNumberOfMessages:int=10, message_attribute_names: list[str] = [])->list[Message]:
    #     try:
    #         res = sqs.client.receive_message(QueueUrl=self.queue.value, MaxNumberOfMessages=MaxNumberOfMessages, MessageAttributeNames=message_attribute_names)
    #         if not res.get("Messages",None): return []
    #         return [Message(**m) for m in res['Messages']]
    #     except Exception as e:
    #         print(e)
    #         raise Exception(e)
    
    # def deleteMessages(self, messages: list[Message]):
    #     sqs.client.delete_message_batch(QueueUrl=self.queue.value, Entries=list(map(lambda x: {"Id": x.messageId, "ReceiptHandle": x.receiptHandle}, messages)))
    
