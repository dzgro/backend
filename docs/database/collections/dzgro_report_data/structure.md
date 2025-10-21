# dzgro_report_data - Structure

## Overview
- **Collection**: `dzgro_report_data`
- **Document Count**: 261
- **Average Document Size**: 360 bytes
- **Total Size**: 94,053 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `68e32feeeb3729c7db7f0e9c`, `68e32feeeb3729c7db7f0e9f`, `68e32feeeb3729c7db7f0e9d`

### `createdat`

- **Type**: `datetime`

### `expense`

- **Type**: `int | float`

### `giftwrapprice`

- **Type**: `int`
- **Sample Values**: `0`, `0`, `0`

### `giftwraptax`

- **Type**: `int`
- **Sample Values**: `0`, `0`, `0`

### `itempromotiondiscount`

- **Type**: `int`
- **Sample Values**: `0`, `0`, `0`

### `netprice`

- **Type**: `float`
- **Sample Values**: `1293.0`, `676.0`, `577.0`

### `netproceeds`

- **Type**: `float`
- **Sample Values**: `1020.41`, `461.01`, `376.56`

### `nettax`

- **Type**: `float`
- **Sample Values**: `138.54`, `72.43`, `61.82`

### `orderdate`

- **Type**: `str`
- **Sample Values**: `2025-08-05T00:27:33.000`, `2025-08-05T08:51:50.000`, `2025-08-05T06:29:11.000`

### `orderid`

- **Type**: `str`
- **Sample Values**: `404-7853082-3804362`, `405-3608308-4675525`, `404-5024889-6478758`

### `price`

- **Type**: `float`
- **Sample Values**: `1293.0`, `676.0`, `577.0`

### `reportid`

- **Type**: `ObjectId`
- **Sample Values**: `68e32fc91275022d4badc612`, `68e32fc91275022d4badc612`, `68e32fc91275022d4badc612`

### `shippingprice`

- **Type**: `int`
- **Sample Values**: `0`, `0`, `0`

### `shippingtax`

- **Type**: `int`
- **Sample Values**: `0`, `0`, `0`

### `shippromotiondiscount`

- **Type**: `int`
- **Sample Values**: `0`, `0`, `0`

### `tax`

- **Type**: `float`
- **Sample Values**: `138.54`, `72.43`, `61.82`


## Sample Documents

### Sample 1

```json
{
  "_id": "68e32feeeb3729c7db7f0e9c",
  "createdat": "2025-10-06T02:56:46.193000",
  "expense": -272.59,
  "giftwrapprice": 0,
  "giftwraptax": 0,
  "itempromotiondiscount": 0,
  "netprice": 1293.0,
  "netproceeds": 1020.41,
  "nettax": 138.54,
  "orderdate": "2025-08-05T00:27:33.000",
  "orderid": "404-7853082-3804362",
  "price": 1293.0,
  "reportid": "68e32fc91275022d4badc612",
  "shippingprice": 0,
  "shippingtax": 0,
  "shippromotiondiscount": 0,
  "tax": 138.54
}
```

### Sample 2

```json
{
  "_id": "68e32feeeb3729c7db7f0e9f",
  "createdat": "2025-10-06T02:56:46.193000",
  "expense": -214.99,
  "giftwrapprice": 0,
  "giftwraptax": 0,
  "itempromotiondiscount": 0,
  "netprice": 676.0,
  "netproceeds": 461.01,
  "nettax": 72.43,
  "orderdate": "2025-08-05T08:51:50.000",
  "orderid": "405-3608308-4675525",
  "price": 676.0,
  "reportid": "68e32fc91275022d4badc612",
  "shippingprice": 0,
  "shippingtax": 0,
  "shippromotiondiscount": 0,
  "tax": 72.43
}
```

