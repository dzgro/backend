from dzgroshared.models.enums import ENVIRONMENT, QueueName, SQSMessageStatus
from pydantic import BaseModel
from dzgroshared.models.sqs import BatchMessageRequest, DeleteMessageBatchRequest, DeleteMessageBatchResponse, DeleteMessageBatchResultEntry, SQSBatchFailedMessage, SQSBatchSendResponse, SQSBatchSuccessMessage, SendMessageRequest, SQSSendMessageResponse, SQSEvent, ReceiveMessageRequest, SQSMessageAttribute, SQSRecord, catch_sqs_exceptions, DeleteMessageBatchEntry, BatchResultErrorEntry
import uuid, botocore.exceptions
from mypy_boto3_sqs import SQSClient
from dzgroshared.client import DzgroSharedClient

class SqsHelper:
    sqsclient: SQSClient

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client

    def __getattr__(self, item):
        return None

    def getClient(self) -> SQSClient:
        if self.sqsclient: 
            return self.sqsclient
        from botocore.config import Config
        from typing import cast
        import boto3
        self.sqsclient = cast(SQSClient, boto3.client('sqs', config=Config(region_name=self.client.REGION)))
        return self.sqsclient
    
    def getQueueUrl(self, queue: QueueName) -> str:
        return f"https://sqs.{self.client.REGION}.amazonaws.com/{self.client.ACCOUNT_ID}/{queue.value}{self.client.env.value}Q"

    @catch_sqs_exceptions
    async def sendMessage(self, payload: SendMessageRequest, MessageBody: BaseModel, extras: dict | None = None) -> str:
        if self.client.env!=ENVIRONMENT.LOCAL:
            client = self.getClient()
            send_args = {
                "QueueUrl": self.getQueueUrl(payload.Queue),
                "MessageBody": MessageBody.model_dump_json(),
                "DelaySeconds": payload.DelaySeconds or 0,
            }
            if payload.MessageAttributes: 
                send_args["MessageAttributes"] = { 
                    key: attr.model_dump(exclude_none=True) 
                    for key, attr in payload.MessageAttributes.items() 
                }
            
            response = client.send_message(**send_args)
            res = SQSSendMessageResponse(
                success=True,
                message_id=response.get("MessageId", ""),
                sequence_number=response.get("SequenceNumber")
            )
        else:
            res = SQSSendMessageResponse(
            success=True,
            message_id=str(uuid.uuid4())
        )

        await self.client.db.sqs_messages.addMessageToDb(res.message_id, payload.Queue, MessageBody, extras)
        return res.message_id

    @catch_sqs_exceptions
    async def sendBatchMessage(self, queue: QueueName, req: list[BatchMessageRequest]) -> SQSBatchSendResponse:
        if not req: raise ValueError("Request list cannot be empty")
        dbBatch: list[dict] = []
        res = SQSBatchSendResponse(Success=[], Failed=[])
        if self.client.env!=ENVIRONMENT.LOCAL:
            client = self.getClient()
            send_args = {
                "QueueUrl": self.getQueueUrl(queue),
                "Entries": [
                    {
                        "Id": entry.Id,
                        "MessageBody": entry.Body.model_dump_json(),
                        "DelaySeconds": entry.DelaySeconds or 0,
                        "MessageAttributes": {
                            key: attr.model_dump(exclude_none=True)
                            for key, attr in entry.MessageAttributes.items()
                        } if entry.MessageAttributes else None
                    }
                    for entry in req
                ]
            }
            response = client.send_message_batch(**send_args)
            res.Failed = [SQSBatchFailedMessage(Id=item['Id'], Code=item['Code'], Message=item.get('Message')) for item in (response.get('Failed', []))]
            res.Success = [SQSBatchSuccessMessage(Id=item['Id'], MessageID=item.get('MessageId')) for item in (response.get('Successful', []))]

            for item in res.Success:
                entry = next((e for e in req if e.Id == item.Id), None)
                if entry:
                    body = { "model": entry.Body.__class__.__name__, "body": entry.Body.model_dump(exclude_none=True), "_id": item.MessageID, "status": SQSMessageStatus.PENDING.value}
                    dbBatch.append(body)
        else:
            for entry in req:
                body = { "model": entry.Body.__class__.__name__, "body": entry.Body.model_dump(exclude_none=True), "_id": str(uuid.uuid4()), "status": SQSMessageStatus.PENDING.value}
                dbBatch.append(body)

        await self.client.db.sqs_messages.addBatchMessageToDb(dbBatch)
        return res
    
    def getSQSEventByMessage(self, message: SQSSendMessageResponse, body: BaseModel):
        return {
            "Records": [
                {
                    "messageId": message.message_id,
                    "receiptHandle": 'rec123',
                    "md5OfBody": 'md5OfBody',
                    "body": body.model_dump_json(exclude_none=True),
                    "messageAttributes": {}
                }
            ]
        }

    @catch_sqs_exceptions
    async def deleteMessage(self, queue: QueueName, receipt_handle: str) -> None:
        try:
            self.getClient().delete_message(
                QueueUrl=self.getQueueUrl(queue),
                ReceiptHandle=receipt_handle
            )
        except botocore.exceptions.ClientError as e:
            
            pass
    
    @catch_sqs_exceptions
    async def deleteMessageBatch(self, req: DeleteMessageBatchRequest) -> DeleteMessageBatchResponse:
        res =  self.getClient().delete_message_batch(
            QueueUrl=req.QueueUrl.value,
            Entries=[{ 'Id': entry.Id, 'ReceiptHandle': entry.ReceiptHandle } for entry in req.Entries]
        )
        return DeleteMessageBatchResponse(
            Successful=[DeleteMessageBatchResultEntry(Id=entry['Id']) for entry in res.get('Successful', [])],
            Failed=[BatchResultErrorEntry(Id=entry['Id'], Code=entry['Code'], SenderFault=entry['SenderFault'], Message=entry.get('Message',None)) for entry in res.get('Failed', [])]
        )

    @catch_sqs_exceptions
    async def getMessages(self, request: ReceiveMessageRequest) -> SQSEvent:
        client = self.getClient()
        
        # Build receive_message arguments
        receive_args: dict = {
            "QueueUrl": request.QueueUrl.value,
        }
        
        if request.MaxNumberOfMessages:
            receive_args["MaxNumberOfMessages"] = request.MaxNumberOfMessages
        if request.MessageAttributeNames:
            receive_args["MessageAttributeNames"] = request.MessageAttributeNames
        if request.AttributeNames:
            receive_args["AttributeNames"] = request.AttributeNames
        if request.VisibilityTimeoutSeconds is not None:
            receive_args["VisibilityTimeoutSeconds"] = request.VisibilityTimeoutSeconds
        if request.WaitTimeSeconds is not None:
            receive_args["WaitTimeSeconds"] = request.WaitTimeSeconds
        if request.ReceiveRequestAttemptId:
            receive_args["ReceiveRequestAttemptId"] = request.ReceiveRequestAttemptId
        
        res = client.receive_message(**receive_args)
        
        messages: list[SQSRecord] = []
        if 'Messages' in res:
            for m in res['Messages']:
                # Convert MessageAttributes to SQSMessageAttribute objects
                message_attrs = {}
                if 'MessageAttributes' in m:
                    for key, attr in m['MessageAttributes'].items():
                        message_attrs[key] = SQSMessageAttribute(
                            stringValue=attr.get('StringValue'),
                            stringListValues=attr.get('StringListValues', []),
                            dataType=attr.get('DataType', 'String')
                        )
                
                message = SQSRecord(
                    messageId=m.get('MessageId', ""),
                    receiptHandle=m.get('ReceiptHandle', ""),
                    md5OfBody=m.get('MD5OfBody', ""),
                    body=m.get('Body', ""),
                    messageAttributes=message_attrs
                )
                messages.append(message)
        
        return SQSEvent(
            Records=messages
        )

