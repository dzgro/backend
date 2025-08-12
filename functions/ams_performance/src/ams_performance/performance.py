from models.enums import AMSDataSet
from db import DbClient
from datetime import datetime, timezone
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
class HourlyPerformance:
    dataSet: AMSDataSet
    sellerid: str
    marketplaceId: str
    dbClient: DbClient

    def __init__(self, db: DbClient, dataSet: AMSDataSet, sellerid: str, marketplaceId: str):
        self.dataSet = dataSet
        self.sellerid = sellerid
        self.marketplaceId = marketplaceId
        self.dbClient = db

    async def execute(self, data: list[dict]):
        parsed_data: list[dict] = []
        for item in data:
            parsed_item:dict = {"_id": item['idempotency_id'],'sellerid': self.sellerid,'marketplaceid': self.marketplaceId}
            
            for k, v in item.items():
                if k=='time_window_start':
                    dt_with_offset = datetime.fromisoformat(v)
                    parsed_item[k] = dt_with_offset.replace(tzinfo=timezone.utc)
                if k in numbers and v>0: parsed_item[k] = v
                if k in keys: parsed_item[keysmapping[k]] = v
            parsed_data.append(parsed_item)
        await self.dbClient.db['hourly_performance'].insert_many(parsed_data)
