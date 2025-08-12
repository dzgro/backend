from models.sqs import SQSEvent
from models.enums import AMSDataSet
from dzgrosecrets import SecretManager
from db import DbClient
MONGOURI = SecretManager().MONGO_DB_CONNECT_URI
db = DbClient(MONGOURI)

def isPerformanceSet(dataset: AMSDataSet)->bool:
    return dataset in [AMSDataSet.SP_TRAFFIC, AMSDataSet.SP_CONVERSIONS, AMSDataSet.SB_TRAFFIC, AMSDataSet.SB_CONVERSIONS, AMSDataSet.SD_TRAFFIC, AMSDataSet.SD_CONVERSIONS]

async def processHourlyPerformance(datasetid: AMSDataSet, sellerid:str, marketplaceid:str, data: list[dict]):
    from ams_performance.performance import HourlyPerformance
    await HourlyPerformance(
        db=db,
        dataSet=datasetid,
        sellerid=sellerid,
        marketplaceId=marketplaceid
    ).execute(data)


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
                        if isPerformanceSet(datasetid):
                            await processHourlyPerformance(datasetid, sellerid, marketplaceid, body.get("data", []))

    except Exception as e:
        print(f"[ERROR] Failed to process message {record.messageId}: {e}")
        
def handler(event, context):
    import asyncio
    asyncio.run(execute(event, context))
    return {
        "statusCode": 200,
        "body": "Processed successfully"
    }