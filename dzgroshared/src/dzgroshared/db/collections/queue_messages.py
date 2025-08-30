from datetime import datetime
from dzgroshared.client import DzgroSharedClient
from dzgroshared.models.sqs import BatchMessageRequest
from pydantic import BaseModel
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType, QueueName, SQSMessageStatus
from dzgroshared.models.collections.queue_messages import MODEL_REGISTRY

class QueueMessagesHelper:
    dbManager: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.dbManager = DbManager(client.db.database.get_collection(CollectionType.QUEUE_MESSAGES.value))

    async def addMessageToDb(self, messageid: str, queue: QueueName,  MessageBody: BaseModel, extras: dict|None = None):
        body = { "model": MessageBody.__class__.__name__, "body": MessageBody.model_dump(exclude_none=True, mode="json"), "_id": messageid, "status": SQSMessageStatus.PENDING.value, "queue": queue.value}
        if extras: body.update(extras)
        return await self.dbManager.insertOne(body)

    async def addBatchMessageToDb(self, batch: list[dict]):
        return await self.dbManager.insertMany(batch)

    async def setMessageAsProcessing(self, messageid: str):
        count, id = await self.dbManager.updateOne({"_id": messageid, "status": SQSMessageStatus.PENDING.value},setDict={"status": SQSMessageStatus.PROCESSING.value})
        if count != 0: raise ValueError(f"Message {messageid} is not in PENDING status")
        return id

    async def setMessageAsCompleted(self, messageid: str, extras: dict ={}):
        setDict = {"status": SQSMessageStatus.COMPLETED.value}
        extras = {f'body.{k}': v for k, v in extras.items()}
        setDict.update(extras)
        return await self.dbManager.updateOne({"_id": messageid}, setDict=setDict, markCompletion=True)

    async def setMessageAsFailed(self, messageid: str, error:str = "No Error Provided", extras: dict ={}):
        setDict = {"status": SQSMessageStatus.FAILED.value, "error": error}
        extras = {f'body.{k}': v for k, v in extras.items()}
        setDict.update(extras)
        return await self.dbManager.updateOne({"_id": messageid}, setDict=setDict)

    async def getMessageStatus(self, messageid:str):
        message = await self.dbManager.findOne({"_id": messageid}, projectionInc=["status"])
        return SQSMessageStatus(message["status"])

    async def addIndex(self, messageid:str, index):
        return await self.dbManager.updateOne({"_id": messageid},setDict={"body.index": index})
    
    def __deserialize_message(self, doc: dict) -> BaseModel:
        model_name = doc.get("model")
        body = doc.get("body")
        if model_name not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {model_name}")
        model_cls = MODEL_REGISTRY[model_name]
        return model_cls.model_validate(body)

    async def getMessagesByIndex(self, index:str):
        result = await self.dbManager.find({"body.index": index})
        return [self.__deserialize_message(doc) for doc in result]
    
    async def getMessage(self, messageid:str, status: SQSMessageStatus|None = None) -> BaseModel:
        filterdict = {"_id": messageid}
        if status: filterdict["status"] = status.value
        message = await self.dbManager.findOne(filterdict)
        return self.__deserialize_message(message)