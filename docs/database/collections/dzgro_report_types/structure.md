# dzgro_report_types - Structure

## Overview
- **Collection**: `dzgro_report_types`
- **Document Count**: 7
- **Average Document Size**: 540 bytes
- **Total Size**: 3,786 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `Order Payment Reconciliation`, `Profitability`, `Inventory Planning`

### `comingsoon`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `description`

- **Type**: `list[]`

### `index`

- **Type**: `int`
- **Sample Values**: `1`, `3`, `4`

### `maxdays`

- **Type**: `int`
- **Sample Values**: `31`, `31`, `31`

### `projection`

- **Type**: `dict`

### `projection.ASIN`

- **Type**: `str`
- **Sample Values**: `$asin`, `$asin`

### `projection.Ad Sales`

- **Type**: `str`
- **Sample Values**: `$sales`

### `projection.Ad Spend`

- **Type**: `str`
- **Sample Values**: `$cost`

### `projection.Average Price`

- **Type**: `str`
- **Sample Values**: `$avgprice`

### `projection.Browser Page Views`

- **Type**: `str`
- **Sample Values**: `$browserpageviews`

### `projection.Browser Page Views %`

- **Type**: `str`
- **Sample Values**: `$browserpageviewspercent`

### `projection.Browser Sessions`

- **Type**: `str`
- **Sample Values**: `$browsersessions`

### `projection.Browser Sessions %`

- **Type**: `str`
- **Sample Values**: `$browsersessionspercent`

### `projection.Buy Box %`

- **Type**: `str`
- **Sample Values**: `$buyboxpercent`

### `projection.Click Through Rate (CTR)`

- **Type**: `str`
- **Sample Values**: `$ctr`

### `projection.Clicks`

- **Type**: `str`
- **Sample Values**: `$clicks`

### `projection.Collation Type`

- **Type**: `str`
- **Sample Values**: `$collatetype`

### `projection.Conversion Ratio (CVR)`

- **Type**: `str`
- **Sample Values**: `$cvr`

### `projection.Cost Per Click (CPC)`

- **Type**: `str`
- **Sample Values**: `$cpc`

### `projection.Current Inventory`

- **Type**: `str`
- **Sample Values**: `$quantity`

### `projection.Data End Date`

- **Type**: `str`
- **Sample Values**: `$enddate`, `$enddate`

### `projection.Data Start Date`

- **Type**: `str`
- **Sample Values**: `$startdate`, `$startdate`

### `projection.Days of Inventory Left`

- **Type**: `str`
- **Sample Values**: `$inventorydays`

### `projection.Expense`

- **Type**: `str`
- **Sample Values**: `$expense`, `$expense`

### `projection.FBA Revenue`

- **Type**: `str`
- **Sample Values**: `$fbarevenue`

### `projection.FBA Revenue %`

- **Type**: `str`
- **Sample Values**: `$fbarevenuepercent`

### `projection.FBM Revenue`

- **Type**: `str`
- **Sample Values**: `$fbmrevenue`

### `projection.FBM Revenue %`

- **Type**: `str`
- **Sample Values**: `$fbmrevenuepercent`

### `projection.Gift Wrap Price`

- **Type**: `str`
- **Sample Values**: `$giftwrapprice`, `$giftwrapprice`

### `projection.Gift Wrap Tax`

- **Type**: `str`
- **Sample Values**: `$giftwraptax`, `$giftwraptax`

### `projection.Impressions`

- **Type**: `str`
- **Sample Values**: `$impressions`

### `projection.Inventory Days Group`

- **Type**: `str`
- **Sample Values**: `$inventorytag`

### `projection.Item Promotion Discount`

- **Type**: `str`
- **Sample Values**: `$itempromotiondiscount`, `$itempromotiondiscount`

### `projection.Mobile App Page Views`

- **Type**: `str`
- **Sample Values**: `$mobileapppageviews`

### `projection.Mobile App Page Views %`

- **Type**: `str`
- **Sample Values**: `$mobileapppageviewspercent`

### `projection.Mobile App Sessions`

- **Type**: `str`
- **Sample Values**: `$mobileappsessions`

### `projection.Mobile App Sessions &`

- **Type**: `str`
- **Sample Values**: `$mobileappsessionspercent`

### `projection.Net Price`

- **Type**: `str`
- **Sample Values**: `$netprice`, `$netprice`

### `projection.Net Proceeds`

- **Type**: `str`
- **Sample Values**: `$netproceeds`, `$netproceeds`, `$netproceeds`

### `projection.Net Proceeds %`

- **Type**: `str`
- **Sample Values**: `$netproceedspercent`

### `projection.Net Tax`

- **Type**: `str`
- **Sample Values**: `$nettax`, `$nettax`

### `projection.Order Date`

- **Type**: `str`
- **Sample Values**: `$orderdate`, `$orderdate`

### `projection.Order Id`

- **Type**: `str`
- **Sample Values**: `$orderid`, `$orderid`

### `projection.Page Views`

- **Type**: `str`
- **Sample Values**: `$pageviews`

### `projection.Price`

- **Type**: `str`
- **Sample Values**: `$price`, `$price`

### `projection.Return %`

- **Type**: `str`
- **Sample Values**: `$returnpercent`

### `projection.Revenue`

- **Type**: `str`
- **Sample Values**: `$revenue`

### `projection.RoAS`

- **Type**: `str`
- **Sample Values**: `$roas`

### `projection.Sessions`

- **Type**: `str`
- **Sample Values**: `$sessions`

### `projection.Shipping Price`

- **Type**: `str`
- **Sample Values**: `$shippingprice`, `$shippingprice`

### `projection.Shipping Promotion Discount`

- **Type**: `str`
- **Sample Values**: `$shippromotiondiscount`, `$shippromotiondiscount`

### `projection.Shipping Tax`

- **Type**: `str`
- **Sample Values**: `$shippingtax`, `$shippingtax`

### `projection.Sku`

- **Type**: `str`
- **Sample Values**: `$sku`, `$sku`

### `projection.TACoS`

- **Type**: `str`
- **Sample Values**: `$tacos`

### `projection.Tax`

- **Type**: `str`
- **Sample Values**: `$tax`, `$tax`

### `projection.Total Units Sold`

- **Type**: `str`
- **Sample Values**: `$netquantity`

### `projection.Unit Session %`

- **Type**: `str`
- **Sample Values**: `$unitsessionpercent`

### `projection.Units Ordered`

- **Type**: `str`
- **Sample Values**: `$soldqty`

### `projection.Units Returned`

- **Type**: `str`
- **Sample Values**: `$returnquantity`

### `projection.Value`

- **Type**: `str`
- **Sample Values**: `$value`


## Sample Documents

### Sample 1

```json
{
  "_id": "Order Payment Reconciliation",
  "description": [
    "Order level report with price, tax, expense and net proceeds from settlements",
    "This file also includes additional shipping, giftwrap and discounts"
  ],
  "maxdays": 31,
  "index": 1,
  "projection": {
    "Order Id": "$orderid",
    "Order Date": "$orderdate",
    "Price": "$price",
    "Tax": "$tax",
    "Gift Wrap Price": "$giftwrapprice",
    "Gift Wrap Tax": "$giftwraptax",
    "Shipping Price": "$shippingprice",
    "Shipping Tax": "$shippingtax",
    "Shipping Promotion Discount": "$shippromotiondiscount",
    "Item Promotion Discount": "$itempromotiondiscount",
    "Net Price": "$netprice",
    "Net Tax": "$nettax",
    "Expense": "$expense",
    "Net Proceeds": "$netproceeds"
  }
}
```

### Sample 2

```json
{
  "_id": "Profitability",
  "description": [
    "Profitability Report at Category, Parent, Asin or Sku level",
    "Report is generated for the specified dates"
  ],
  "maxdays": 31,
  "comingsoon": true,
  "index": 3
}
```

