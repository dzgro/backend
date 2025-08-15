from dzgroshared.functions import FunctionClient
from dzgroshared.models.sqs import SQSEvent
from dzgroshared.models.enums import AMSDataSet

def isChangeSet(dataset: AMSDataSet)->bool:
    return dataset in [AMSDataSet.CAMPAIGNS, AMSDataSet.AD_GROUPS, AMSDataSet.ADS, AMSDataSet.TARGETS]
    
async def processChangeSet(client: FunctionClient, datasetid: AMSDataSet, sellerid:str, marketplaceid:str, body: dict):
    from dzgroshared.functions.ams_change.change_sets import ChangeSet
    change_set = ChangeSet(
        client=client,
        dataSet=datasetid,
        sellerid=sellerid,
        marketplaceId=marketplaceid,
        body=body
    )
    await change_set.execute()


async def execute(client: FunctionClient):
    try:
        parsed = SQSEvent.model_validate(client.event)
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
                            await processChangeSet(client, datasetid, sellerid, marketplaceid, body)
                        
    except Exception as e:
        print(f"[ERROR] Failed to process message {record.messageId}: {e}")