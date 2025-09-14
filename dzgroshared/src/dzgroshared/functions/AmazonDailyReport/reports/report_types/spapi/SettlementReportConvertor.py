
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field
from dzgroshared.db.settlements.model import Settlement

class FileSettlement(BaseModel):
    settlementId:str =  Field(validation_alias='settlement-id')
    startDate:str =  Field(validation_alias='settlement-start-date')
    endDate:str =  Field(validation_alias='settlement-end-date')
    depositDate:str =  Field(validation_alias='deposit-date')
    totalAmount:str =  Field(validation_alias='total-amount')
    currency:str =  Field(validation_alias='currency')
    transactionType:str =  Field(validation_alias='transaction-type', default="Other")
    orderId:str =  Field(validation_alias='order-id')
    merchantOrderId:str =  Field(validation_alias='merchant-order-id')
    adjustmentId:str =  Field(validation_alias='adjustment-id')
    shipmentId:str =  Field(validation_alias='shipment-id')
    amountType:str =  Field(validation_alias='amount-type', default="Other")
    marketplaceName:str =  Field(validation_alias='marketplace-name')
    amountDescription:str =  Field(validation_alias='amount-description')
    amount:str =  Field(validation_alias='amount')
    fulfillmentId:str =  Field(validation_alias='fulfillment-id')
    orderItemId:str =  Field(validation_alias='order-item-code')
    postedDate:str =  Field(validation_alias='posted-date')
    postedDateTime:str =  Field(validation_alias='posted-date-time')
    merchantOrderItemId:str =  Field(validation_alias='merchant-order-item-id')
    merchantAdjustmentItemId:str =  Field(validation_alias='merchant-adjustment-item-id')
    sku:str =  Field(validation_alias='sku')
    quantity:str =  Field(validation_alias='quantity-purchased')
    promotionId:str =  Field(validation_alias='promotion-id')

class SettlementReportConvertor:
    

    def __init__(self) -> None:
        pass
    
    def convertFileRowToSettlement(self, x: FileSettlement)->Settlement:
        depositDate = datetime.strptime(x.depositDate, "%d.%m.%Y %H:%M:%S %Z") if len(x.depositDate.strip())>0 else None
        startDate = datetime.strptime(x.startDate, "%d.%m.%Y %H:%M:%S %Z") if len(x.startDate.strip())>0 else None
        endDate = datetime.strptime(x.endDate, "%d.%m.%Y %H:%M:%S %Z") if len(x.endDate.strip())>0 else None
        totalAmount = float(x.totalAmount) if len(x.totalAmount.strip())>0 else None
        orderId = x.orderId if len(x.orderId.strip())>0 else None
        orderItemId = x.orderItemId if len(x.orderItemId.strip())>0 else None
        sku = x.sku if len(x.sku.strip())>0 else None
        transactionType: str = x.transactionType if len(x.transactionType.strip())>0 else 'Other'
        amountType: str = x.amountType if len(x.amountType.strip())>0 else 'Other'
        amountDescription = x.amountDescription if len(x.amountDescription.strip())>0 else None
        amount = float(x.amount) if len(x.amount.strip())>0 else 0
        date = datetime.strptime(x.postedDate, "%d.%m.%Y") if len(x.postedDate.strip())>0 else None
        return Settlement(settlementid=x.settlementId, orderitemid=orderItemId, depositdate=depositDate,startdate=startDate,enddate=endDate, totalamount=totalAmount, orderid=orderId, sku=sku, transactiontype=transactionType, amounttype=amountType, amountdescription=amountDescription, amount=amount, date=date )


    def convert(self, data: list[dict], settlementIds: list[str]):
        if len(data)>0 and data[0]['settlement-id'] not in settlementIds:
            fileSettlements: list[FileSettlement] = list(map(lambda x: FileSettlement(**x), data))
            settlements: list[Settlement] = [self.convertFileRowToSettlement(row) for row in fileSettlements]
            return settlements
        return []
