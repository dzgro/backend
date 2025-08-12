from models.sqs import SQSEvent
from models.enums import AMSDataSet
from dzgrosecrets import SecretManager
from db import DbClient
MONGOURI = SecretManager().MONGO_DB_CONNECT_URI
db = DbClient(MONGOURI)

def isChangeSet(dataset: AMSDataSet)->bool:
    return dataset in [AMSDataSet.CAMPAIGNS, AMSDataSet.AD_GROUPS, AMSDataSet.ADS, AMSDataSet.TARGETS]
    
async def processChangeSet(datasetid: AMSDataSet, sellerid:str, marketplaceid:str, body: dict):
    from ams_change.change_sets import ChangeSet
    change_set = ChangeSet(
        db=db,
        dataSet=datasetid,
        sellerid=sellerid,
        marketplaceId=marketplaceid,
        body=body
    )
    await change_set.execute()


async def execute(event: dict, context):
    try:
        parsed = SQSEvent.model_validate(event)
        for record in parsed.Records:
            if record.dictBody:
                body = record.dictBody
                SubscribeURL = body.get("SubscribeURL", None)
                if SubscribeURL:
                    import urllib.request
                    urllib.request.urlopen(SubscribeURL)
                else:
                    datasetid = AMSDataSet(body.get("dataset_id"))
                    sellerid = body.get("advertiser_id", None)
                    marketplaceid = body.get("marketplace_id", None)
                    if sellerid and marketplaceid:
                        if isChangeSet(datasetid):
                            await processChangeSet(datasetid, sellerid, marketplaceid, body)
                        
    except Exception as e:
        print(f"[ERROR] Failed to process message {record.messageId}: {e}")
        
def handler(event, context):
    import asyncio
    asyncio.run(execute(event, context))
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }