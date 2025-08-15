
from pydantic import BaseModel
import json
from dzgroshared.models.sqs import aws_error_handler, SendMessageRequest, SQSSendMessageResponse
import uuid
from mypy_boto3_sqs import SQSClient
from dzgroshared.client import DzgroSharedClient

            

class SqsHelper:
    client: DzgroSharedClient
    sqsclient: SQSClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client

    def getClient(self):
        if self.sqsclient: return self.sqsclient
        from botocore.config import Config
        from typing import cast
        import boto3
        self.sqsclient = cast(SQSClient, boto3.client('sqs', config=Config(region_name = 'ap-south-1')))
        return self.sqsclient
        

    @aws_error_handler()
    async def sendMessage(self, payload: SendMessageRequest, MessageBody: BaseModel)->SQSSendMessageResponse:
        send_args = {
            "QueueUrl": payload.QueueUrl.value,
            "MessageBody": json.dumps(MessageBody),
            "DelaySeconds": payload.DelaySeconds or 0,
        }
        if payload.MessageAttributes: send_args["MessageAttributes"] = { key: attr.model_dump(exclude_none=True) for key, attr in payload.MessageAttributes.items() }
        if self.sqsclient is None:
            raise RuntimeError("SQS client is not initialized.")
        response = self.sqsclient.send_message(**send_args)
        res = SQSSendMessageResponse(
            success=True,
            message_id=response.get("MessageId"),
            sequence_number=response.get("SequenceNumber")
        )
        await self.client.db.sqs_messages().addMessageToDb(res.message_id, MessageBody)
        return res
    
    async def mockMessage(self, payload: SendMessageRequest, MessageBody: BaseModel)->SQSSendMessageResponse:
        res = SQSSendMessageResponse(
            success=True,
            message_id=str(uuid.uuid4())
        )
        await self.client.db.sqs_messages().addMessageToDb(res.message_id, MessageBody)
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
    
