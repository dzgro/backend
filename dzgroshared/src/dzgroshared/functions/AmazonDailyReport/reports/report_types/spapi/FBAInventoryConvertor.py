from datetime import datetime
from dzgroshared.db.collections.storage_fees import FnSkuStorageFees
from dzgroshared.utils import date_util
from dzgroshared.models.enums import MarketplaceId
from dzgroshared.models.extras.amazon_daily_report import MarketplaceObjectForReport
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.models.collections.orders import DbOrder, DbOrderItem
from typing import Optional



class FBAInventoryConvertor:
    marketplace: MarketplaceObjectForReport
    

    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace

    def convert(self, data: list[dict]):
        try:
            return [{"sku": item['sku'], "fnsku": item['fnsku'], "asin": item['asin']} for item in data]
        except Exception as e:
            print(f"Error in converting FBA Storage Fees: {e}")
            print(data)
            return []
    
    