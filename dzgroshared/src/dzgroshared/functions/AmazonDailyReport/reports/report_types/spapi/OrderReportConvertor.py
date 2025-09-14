from datetime import datetime
from dzgroshared.utils import date_util
from dzgroshared.db.enums import MarketplaceId
from dzgroshared.db.daily_report_group.model import MarketplaceObjectForReport
from pydantic import BaseModel, Field
from dzgroshared.db.orders.model import DbOrder, DbOrderItem


class FileOrder(BaseModel):
    orderId:str = Field(validation_alias='amazon-order-id')
    purchaseDate:str =  Field(validation_alias='purchase-date')
    lastUpdateDate:str =  Field(validation_alias='last-updated-date')
    orderStatus:str =  Field(validation_alias='order-status')
    fulfillmentChannel:str =  Field(validation_alias='fulfillment-channel')
    salesChannel:str =  Field(validation_alias='sales-channel')
    orderChannel:str =  Field(validation_alias='order-channel')
    shipServiceLevel:str =  Field(validation_alias='ship-service-level')
    productName:str =  Field(validation_alias='product-name')
    sku:str =  Field(validation_alias='sku')
    asin:str =  Field(validation_alias='asin')
    itemStatus:str =  Field(validation_alias='item-status')
    quantity:str =  Field(validation_alias='quantity')
    currency:str =  Field(validation_alias='currency')
    itemPrice:str =  Field(validation_alias='item-price')
    itemTax:str =  Field(validation_alias='item-tax')
    shippingPrice:str =  Field(validation_alias='shipping-price')
    shippingTax:str =  Field(validation_alias='shipping-tax')
    giftWrapPrice:str =  Field(validation_alias='gift-wrap-price')
    giftWrapTax:str =  Field(validation_alias='gift-wrap-tax')
    itemPromotionDiscount:str =  Field(validation_alias='item-promotion-discount')
    shipPromotionDiscount:str =  Field(validation_alias='ship-promotion-discount')
    shipCity:str =  Field(validation_alias='ship-city')
    shipState:str =  Field(validation_alias='ship-state')
    shipPostalCode:str =  Field(validation_alias='ship-postal-code')
    shipCountry:str =  Field(validation_alias='ship-country')
    promotionIds:str =  Field(validation_alias='promotion-ids')
    isBusinessOrder:str =  Field(validation_alias='is-business-order')
    isReplacementOrder:str =  Field(validation_alias='is-replacement-order')
    originalOrderId:str =  Field(validation_alias='original-order-id')
    isTransparency:str =  Field(validation_alias='is-transparency')
    isIba:str =  Field(validation_alias='is-iba')
    numberOfItems:str =  Field(validation_alias='number-of-items')

class OrderReportConvertor:
    marketplace: MarketplaceObjectForReport
    hasIndiaCountry: bool = False

    def __init__(self, marketplace: MarketplaceObjectForReport) -> None:
        self.marketplace = marketplace
        self.hasIndiaCountry = self.marketplace.marketplaceid==MarketplaceId.IN

    
    def getFloatOrNone(self, val: str):
        if len(val.strip())>0: return float(val)
    
    def getStrOrNone(self, val: str):
        if len(val.strip())>0: return val

    def getOrderItem(self, order: FileOrder, id: str, date: datetime):
        price = self.getFloatOrNone(order.itemPrice) or 0
        tax = self.getFloatOrNone(order.itemTax) or 0
        shippingPrice = self.getFloatOrNone(order.shippingPrice)
        shippingTax = self.getFloatOrNone(order.shippingTax)
        giftWrapPrice = self.getFloatOrNone(order.giftWrapPrice)
        giftWrapTax = self.getFloatOrNone(order.giftWrapTax)
        itemPromotionDiscount = self.getFloatOrNone(order.itemPromotionDiscount)
        shipPromotionDiscount = self.getFloatOrNone(order.shipPromotionDiscount)
        revenue = price-(itemPromotionDiscount or 0)-(shipPromotionDiscount or 0)+(giftWrapPrice or 0)
        quantity = int(self.getFloatOrNone(order.quantity) or 0)
        itemStatus = self.getStrOrNone(order.itemStatus)
        return DbOrderItem(order=id,date=date,revenue=revenue,sku=order.sku, itemstatus=itemStatus, asin=order.asin, price=price, tax=tax, quantity=quantity, shippingprice=shippingPrice,shippingtax=shippingTax, giftwrapprice=giftWrapPrice,giftwraptax=giftWrapTax, itempromotiondiscount=itemPromotionDiscount, shippromotiondiscount=shipPromotionDiscount)



    def convert(self, data: list[dict]):
        orderItems: list[DbOrderItem] = []
        orders: list[DbOrder] = []
        processedOrderIds: list[str] = []
        for item in data:
            orderDate = date_util.convertToDate(item['purchase-date'], "%Y-%m-%dT%H:%M:%S%z")
            date = date_util.normalize_date_to_midnight(item['purchase-date'], self.marketplace.details.timezone)
            fOrder = FileOrder(**item)
            state = fOrder.shipState.title() if len(fOrder.shipState.strip())>0 else "Unspecified"
            country = fOrder.shipCountry if len(fOrder.shipCountry.strip())>0 else "Unspecified"
            orderStatus = fOrder.orderStatus
            fulfillment=fOrder.fulfillmentChannel
            orderId = fOrder.orderId
            id = f'{str(self.marketplace.id)}_{orderId}'
            orderItems.append(self.getOrderItem(fOrder, id, date))
            if orderId not in processedOrderIds:
                city = fOrder.shipCity.title() if len(fOrder.shipCity.strip())>0 else None
                code = fOrder.shipPostalCode if len(fOrder.shipPostalCode.strip())>0 else None
                originalOrderId = fOrder.originalOrderId if len(fOrder.originalOrderId.strip())>0 else None
                isBusinessOrder = fOrder.isBusinessOrder=="TRUE" or None
                order = DbOrder(_id=id,orderid=orderId, orderdate=orderDate,date=date, city=city, state=state, country=country, code=code, originalorderid=originalOrderId, fulfillment=fulfillment, orderstatus=orderStatus, isbusinessorder=isBusinessOrder)
                orders.append(order)
                processedOrderIds.append(orderId)
        return orders, orderItems
    
    
    # def getOrderItems(self, orderId: str):
    #     result = self.api.getOrderItems(orderId)
    #     if result.statusCode==429:
    #         time.sleep(1)
    #         return self.getOrderItems(orderId)
    #     elif result.statusCode==200:
    #         return GetOrderItemsResponse(**result.dictResult)
    #     else: raise ValueError(result.error or 'Error in fetching order items')


    # def updateOrderItemIds(self):
    #     filterDict = { 'uid': self.reportUtil.uid, 'marketplace': self.reportUtil.marketplace, 'collection': 'order_items' }
    #     pipeline = [ {'$match': filterDict}, { '$group': { '_id': '$orderid', 'skus': { '$push': '$sku' }, 'distinctSkus': { '$addToSet': '$sku' }, 'orderItemId': { '$push': '$orderitemid' } } }, { '$set': { 'skus': { '$size': '$skus' }, 'distinctSkus': { '$size': '$distinctSkus' }, 'orderItemIds': { '$size': '$orderItemId' } } }, { '$match': { '$expr': { '$and': [ { '$ne': [ '$skus', '$distinctSkus' ] }, {"$eq": ["$orderItemIds",0]} ] } } }, { '$project': { '_id': 1 } }, { '$group': { '_id': None, 'ids': { '$push': '$_id' }, 'count': { '$sum': 1 } } }, { '$project': { '_id': 0 } } ]
    #     data = self.reportUtil.aggregate(pipeline)
    #     if len(data)>0:
    #         orderIds = data[0]['ids']
    #         while len(orderIds)>0:
    #             id = orderIds.pop()
    #             orderItems = self.getOrderItems(id)
    #             for item in orderItems.payload.OrderItems:
    #                 tax = float(item.ItemTax.Amount) if item.ItemTax and item.ItemTax.Amount else 0
    #                 tempFilterDict: dict = {**filterDict, 'orderid':id, "tax":tax, "orderitemid": {"$exists": False}, 'sku':item.SellerSKU}
    #                 updateDict: dict = {'orderitemid':item.OrderItemId}
    #                 self.reportUtil.updateOne(tempFilterDict, updateDict)
                    
    # def merge(self):
    #     self.updateOrderItemIds()
    #     setDict = { 'date': { '$dateFromString': { 'dateString': { '$dateToString': { 'date': '$$ROOT.orderdate', 'timezone': self.marketplace.details.timezone, 'format': '%Y-%m-%d' } } } } }
    #     self.reportUtil.mergeToCollection(CollectionType.ORDER_ITEMS, ['$orderid', '_', '$sku'], setDict, ['$orderitemid'])
    #     self.reportUtil.mergeToCollection(CollectionType.ORDERS, ['$orderid'], setDict)
    #     self.setStates()

    # def setStates(self):
    #     if self.hasIndiaCountry: PipelineProcessor(self.reportUtil.marketplace, self.reportUtil.uid).replaceStateNames()
            

    