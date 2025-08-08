from db.collections.user import AsyncIOMotorDatabase
from pydantic import BaseModel
from db.DbUtils import DbManager
from models.enums import CollectionType, SQSMessageStatus
from models.collections.queue_messages import MODEL_REGISTRY

class QueueMessagesHelper:
    dbManager: DbManager

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.dbManager = DbManager(db.get_collection(CollectionType.QUEUE_MESSAGES.value))

    async def addMessageToDb(self, messageid: str, MessageBody: BaseModel):
        body = { "model": MessageBody.__class__.__name__, "body": MessageBody.model_dump(exclude_none=True), "_id": messageid, "status": SQSMessageStatus.PENDING.value}
        return await self.dbManager.insertOne(body)

    async def setMessageAsProcessing(self, messageid: str):
        await self.dbManager.updateOne({"_id": messageid},setDict={"status": SQSMessageStatus.PROCESSING.value})

    async def setMessageAsCompleted(self, messageid: str):
        await self.dbManager.updateOne({"_id": messageid},setDict={"status": SQSMessageStatus.COMPLETED.value})

    async def setMessageAsFailed(self, messageid: str, error):
        await self.dbManager.updateOne({"_id": messageid},setDict={"status": SQSMessageStatus.FAILED.value, "error": error or "No Error Provided"})
    
    async def getMessageStatus(self, messageid:str):
        message = await self.dbManager.findOne({"_id": messageid}, projectionInc=["status"])
        return SQSMessageStatus(message["status"])

    async def addIndex(self, messageid:str, index):
        return await self.dbManager.updateOne({"_id": messageid},setDict={"body.index": index})

    async def getMessagesByIndex(self, index:str):
        def deserialize_message(doc: dict) -> BaseModel:
            model_name = doc.get("model_name")
            body = doc.get("body")
            if model_name not in MODEL_REGISTRY:
                raise ValueError(f"Unknown model: {model_name}")
            model_cls = MODEL_REGISTRY[model_name]
            return model_cls.model_validate(body)
        result = await self.dbManager.find({"index": index})
        return [deserialize_message(doc) for doc in result]
