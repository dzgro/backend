from pandas import DataFrame
from dzgroshared.models.collections.dzgro_reports import DzgroReportType

all_cols = {
    "expense": "Expense",
    "fulfillment": "Fulfillment",
    "giftwrapprice": "Gift Wrap Price",
    "giftwraptax": "Gift Wrap Tax",
    "itempromotiondiscount": "Item Promotion Discount",
    "netprice": "Net Price",
    "netproceeds": "Net Proceeds",
    "nettax": "Net Tax",
    "orderdate": "Order Date",
    "orderstatus": "Order Status",
    "price": "Price",
    "shippingprice": "Shipping Price",
    "shippingtax": "Shipping Tax",
    "shippromotiondiscount": "Ship Promotion Discount",
    "state": "State",
    "tax": "Tax",
    "orderid": "Order Id",
    "orderdate": "Order Date",
    "orderstatus": "Order Status",
    "sku": "Sku",
    "asin": "ASIN",
    "quantity": "Quantity",
    "soldqty": "Sold Quantity in Last 30 Days",
    "inventorydays": "Number of days of Inventory Left",
    "inventorytag": "Grouped Days",
}

columnsByReportType: dict[DzgroReportType, list[str]] = {
    DzgroReportType.PAYMENT_RECON: ['orderid', 'orderstatus','orderdate', 'fulfillment','state', 'price', 'tax', 'giftwrapprice', 'giftwraptax', 'shippingprice', 'shippingtax','itempromotiondiscount',  'shippromotiondiscount','netprice', 'nettax','expense', 'netproceeds'],
    DzgroReportType.OUT_OF_STOCK: ["sku","asin","quantity"],
    DzgroReportType.INVENTORY_PLANNING: ["sku","asin","quantity","soldqty","inventorydays","inventorytag"],
}

def convertDataFrame(df: DataFrame, reportType: DzgroReportType):
    allColumns = list(df.columns)
    colOrders = columnsByReportType[reportType]
    colOrders = [x for x in colOrders if x in allColumns]
    df = df[colOrders]
    newNames = {c: all_cols[c] for c in colOrders}
    df = df.rename(columns=newNames)
    return df
        


