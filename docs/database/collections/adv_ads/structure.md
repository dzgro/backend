# adv_ads - Structure

## Overview
- **Collection**: `adv_ads`
- **Document Count**: 244
- **Average Document Size**: 359 bytes
- **Total Size**: 87,626 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826_460898982228835`, `6895638c452dc4315750e826_94587703715121`, `6895638c452dc4315750e826_375455047638150`

### `count`

- **Type**: `int`
- **Sample Values**: `1`, `1`, `1`

### `products`

- **Type**: `list[]`

### `products.asin`

- **Type**: `str`
- **Sample Values**: `B07X1271QC`, `B0C739QDTP`, `B0CBGWFVBF`

### `products.image`

- **Type**: `str`
- **Sample Values**: `https://m.media-amazon.com/images/I/61ElPjS3W8L.jpg`, `https://m.media-amazon.com/images/I/71CpH2Mx-7L.jpg`, `https://m.media-amazon.com/images/I/91x51LhIJeL.jpg`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826_460898982228835",
  "count": 1,
  "products": [
    {
      "asin": "B07X1271QC",
      "image": "https://m.media-amazon.com/images/I/61ElPjS3W8L.jpg"
    }
  ]
}
```

### Sample 2

```json
{
  "_id": "6895638c452dc4315750e826_94587703715121",
  "count": 1,
  "products": [
    {
      "asin": "B0C739QDTP",
      "image": "https://m.media-amazon.com/images/I/71CpH2Mx-7L.jpg"
    }
  ]
}
```

