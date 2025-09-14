from datetime import datetime
from dzgroshared.db.collections.storage_fees import FnSkuStorageFees
from dzgroshared.utils import date_util
from dzgroshared.db.enums import MarketplaceId
from dzgroshared.db.daily_report_group.model import MarketplaceObjectForReport
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema
from dzgroshared.db.orders.model import DbOrder, DbOrderItem
from typing import Optional


class InventoryStorageFeeRecord(BaseModel):
    asin: str
    month_of_charge: str
    fnsku: str
    estimated_monthly_storage_fee: float = 0
    fulfillment_center: str
    estimated_total_item_volume: float = 0
    storage_rate: float = 0
    

class FBAStorageReportConvertor:
    marketplace: MarketplaceObjectForReport
    

    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace

    
    def getFloatOrNone(self, val: str|float):
        if isinstance(val, float): return val
        elif isinstance(val, str):
            if len(val.strip())>0: return float(val)
    
    def getStrOrNone(self, val: str):
        if len(val.strip())>0: return val

    def getFnSkuMonthFees(self, fee: InventoryStorageFeeRecord):
        return FnSkuStorageFees(
            _id=f'{str(self.marketplace.id)}_{fee.fnsku}_{fee.month_of_charge}',
            fnsku=fee.fnsku,
            asin=fee.asin,
            date=fee.month_of_charge,
            fees=fee.estimated_monthly_storage_fee,
            center=fee.fulfillment_center
        )


    def convert(self, data: list[dict]):
        try:
            return [self.getFnSkuMonthFees(InventoryStorageFeeRecord.model_validate(item)) for item in data]
        except Exception as e:
            print(f"Error in converting FBA Storage Fees: {e}")
            print(data)
            return []
    
    