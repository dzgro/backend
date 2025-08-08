from db import DbClient
from dzgrosecrets import SecretManager
from models.collections.queue_messages import NewUserQueueMessage, UserDetails
MONGO_DB_URI = SecretManager().MONGO_DB_CONNECT_URI
import json, asyncio

async def handler(event: dict, context):
    if(event['triggerSource'] == "PostConfirmation_ConfirmSignUp"):
        user_attributes = event['request']['userAttributes']
        uid = user_attributes['userName']
        details = UserDetails(**{
                    "name": user_attributes.get('name'),
                    "email": user_attributes.get('email'),
                    "phone": user_attributes.get("phone_number"),
                    "userpoolid": event['userPoolId']
                })
        body = NewUserQueueMessage(index=uid, uid=uid, details=details)
    asyncio.run(sendMessage(body))

async def sendMessage(body: NewUserQueueMessage):
    from sqs import SqsHelper
    from sqs.model import SendMessageRequest, QueueUrl
    req = SendMessageRequest(QueueUrl=QueueUrl.NEW_USER)
    messageid = SqsHelper().sendMessage(req, body).message_id
    await DbClient(MONGO_DB_URI).sqs_messages(body.uid).addMessageToDb(messageid, body)