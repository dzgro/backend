from datetime import datetime, timezone
from dzgroshared.functions import FunctionHandler
from dzgroshared.models.sqs import SQSEvent

numbers: list[str] = ['impressions','cost','clicks', "time_window_start"]
keysmapping = {
    'keyword_id': 'keywordid',
    'target_id': 'targetid',
    'ad_id': 'adid',
    'ad_group_id': 'adgroupid',
    'campaign_id': 'campaignid',
    'placement': 'placement',
    'attributed_conversions_14d': 'orders',
    'attributed_conversions_14d_same_sku': 'orderssku',
    'attributed_sales_14d': 'sales',
    'attributed_sales_14d_same_sku': 'salessku',
    'attributed_units_ordered_14d': 'units',
    'attributed_units_ordered_14d_same_sku': 'unitssku'
}
keys = list(keysmapping.keys())

class AmsPerformanceProcessor:
    body: dict
    fnclient: FunctionHandler

    def __init__(self, client: FunctionHandler):
        self.fnclient = client

    async def execute(self):
        data: list[dict] = []
        try:
            parsed = SQSEvent.model_validate(self.fnclient.event)
            for record in parsed.Records:
                if record.dictBody:
                    body = record.dictBody
                    SubscribeURL = body.get("SubscribeURL", None)
                    if SubscribeURL:
                        import urllib.request
                        urllib.request.urlopen(SubscribeURL)
                    else:
                        data.append(body)
            if data: await self.processList(data)
        except Exception as e:
            print(f"[ERROR] Failed to process message {record.messageId}: {e}")

    async def processList(self, data: list[dict]):
        parsed_data: list[dict] = []
        for item in data:
            parsed_item:dict = {"_id": item['idempotency_id'],'sellerid': item.get("advertiser_id", None),'marketplaceid': item.get("marketplace_id", None)}
            for k, v in item.items():
                if k=='time_window_start':
                    dt_with_offset = datetime.fromisoformat(v)
                    parsed_item[k] = dt_with_offset.replace(tzinfo=timezone.utc)
                if k in numbers and v>0: parsed_item[k] = v
                if k in keys: parsed_item[keysmapping[k]] = v
            parsed_data.append(parsed_item)
        await self.fnclient.client.db.database['hourly_performance'].insert_many(parsed_data)