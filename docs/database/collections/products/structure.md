# products - Structure

## Overview
- **Collection**: `products`
- **Document Count**: 22,437
- **Average Document Size**: 1098 bytes
- **Total Size**: 24,644,630 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `6895638c452dc4315750e826_MAD 2118`, `6895638c452dc4315750e826_MAD 2139`, `6895638c452dc4315750e826_MAD 2143`

### `asin`

- **Type**: `str`
- **Sample Values**: `B07GFLHFB2`, `B07GFQKJ8T`, `B07GFS8BLZ`

### `fulfillment`

- **Type**: `str`
- **Sample Values**: `DEFAULT`, `DEFAULT`, `DEFAULT`

### `images`

- **Type**: `list[]`

### `lastUpdatedDate`

- **Type**: `datetime`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`, `6895638c452dc4315750e826`, `6895638c452dc4315750e826`

### `parentasin`

- **Type**: `str`
- **Sample Values**: `B0CK9W57BL`, `B0CK7WBJH7`, `B0CKB12HQY`

### `parentsku`

- **Type**: `str`
- **Sample Values**: `Mad 2118-$P`, `Mad 2139-$P`, `Mad 2143-$P`

### `price`

- **Type**: `float`
- **Sample Values**: `299.0`, `299.0`, `299.0`

### `producttype`

- **Type**: `str`
- **Sample Values**: `WALL_ART`, `WALL_ART`, `WALL_ART`

### `quantity`

- **Type**: `int`
- **Sample Values**: `10000`, `10000`, `10000`

### `sku`

- **Type**: `str`
- **Sample Values**: `MAD 2118`, `MAD 2139`, `MAD 2143`

### `status`

- **Type**: `str`
- **Sample Values**: `Active`, `Active`, `Active`

### `title`

- **Type**: `str`
- **Sample Values**: `Mad Masters Lord Shri Krishna Painting Aesthetic Hanging Photo Frame Decorative Item Home Decoration and Wall Decor for Living Room and Bedroom (MM 2118, 8x12 Inch, Paper, Without Plexi Glass)`, `Mad Masters Lord Shri Krishna Painting Aesthetic Hanging Photo Frame Decorative Item Home Decoration and Wall Decor for Living Room and Bedroom (MM 2139, 8x12 Inch, Paper, Without Plexi Glass)`, `Mad Masters Lord Shri Radha Krishna Painting Hanging Photo Frame Decorative Item for Living Room, Bedroom, Home Decor and Wall Decoration (MM 2143, 8x12 Inch, Paper, Without Plexi Glass)`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`, `41e34d1a-6031-70d2-9ff3-d1a704240921`

### `variationdetails`

- **Type**: `list[]`

### `variationdetails.customer_package_type`

- **Type**: `str`
- **Sample Values**: `Without Plexi Glass`, `Without Plexi Glass`, `Without Plexi Glass`

### `variationdetails.size`

- **Type**: `str`
- **Sample Values**: `63X33`, `48X22`, `63X33`

### `variationtheme`

- **Type**: `str`
- **Sample Values**: `SIZE_NAME/STYLE_NAME/CUSTOMER_PACKAGE_TYPE`, `SIZE_NAME/STYLE_NAME/CUSTOMER_PACKAGE_TYPE`, `SIZE_NAME/STYLE_NAME/CUSTOMER_PACKAGE_TYPE`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826_MAD 2118",
  "asin": "B07GFLHFB2",
  "fulfillment": "DEFAULT",
  "marketplace": "6895638c452dc4315750e826",
  "price": 299.0,
  "quantity": 10000,
  "sku": "MAD 2118",
  "status": "Active",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "images": [
    "https://m.media-amazon.com/images/I/7131SFFOtAL.jpg",
    "https://m.media-amazon.com/images/I/81YgLPrQGOL.jpg",
    "https://m.media-amazon.com/images/I/71-sTpj3NwL.jpg",
    "https://m.media-amazon.com/images/I/71Hiz76eT0L.jpg",
    "https://m.media-amazon.com/images/I/71sQYLaFxoL.jpg",
    "https://m.media-amazon.com/images/I/71S44q6lONL.jpg",
    "https://m.media-amazon.com/images/I/71S5IiaQ2qL.jpg",
    "https://m.media-amazon.com/images/I/71T1B2x90WL.jpg",
    "https://m.media-amazon.com/images/I/61APzuJpVeL.jpg"
  ],
  "lastUpdatedDate": "2024-12-11T03:52:36.787000",
  "producttype": "WALL_ART",
  "title": "Mad Masters Lord Shri Krishna Painting Aesthetic Hanging Photo Frame Decorative Item Home Decoration and Wall Decor for Living Room and Bedroom (MM 2118, 8x12 Inch, Paper, Without Plexi Glass)",
  "variationdetails": [
    {
      "customer_package_type": "Without Plexi Glass"
    },
    {
      "size": "8 x 12 inches"
    },
    {
      "style": "Paper"
    }
  ],
  "variationtheme": "SIZE_NAME/STYLE_NAME/CUSTOMER_PACKAGE_TYPE",
  "parentasin": "B0CK9W57BL",
  "parentsku": "Mad 2118-$P"
}
```

### Sample 2

```json
{
  "_id": "6895638c452dc4315750e826_MAD 2139",
  "asin": "B07GFQKJ8T",
  "fulfillment": "DEFAULT",
  "marketplace": "6895638c452dc4315750e826",
  "price": 299.0,
  "quantity": 10000,
  "sku": "MAD 2139",
  "status": "Active",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921",
  "images": [
    "https://m.media-amazon.com/images/I/61Rzdig+XcL.jpg",
    "https://m.media-amazon.com/images/I/71MzhipV5mL.jpg",
    "https://m.media-amazon.com/images/I/61im2iefDvL.jpg",
    "https://m.media-amazon.com/images/I/71rTU2u9w-L.jpg",
    "https://m.media-amazon.com/images/I/71GTIiINVBL.jpg",
    "https://m.media-amazon.com/images/I/71Nb1sM5AuL.jpg",
    "https://m.media-amazon.com/images/I/71tyROiABUL.jpg",
    "https://m.media-amazon.com/images/I/71pKAht2ZkL.jpg",
    "https://m.media-amazon.com/images/I/61APzuJpVeL.jpg"
  ],
  "lastUpdatedDate": "2025-04-14T13:38:55.939000",
  "producttype": "WALL_ART",
  "title": "Mad Masters Lord Shri Krishna Painting Aesthetic Hanging Photo Frame Decorative Item Home Decoration and Wall Decor for Living Room and Bedroom (MM 2139, 8x12 Inch, Paper, Without Plexi Glass)",
  "variationdetails": [
    {
      "customer_package_type": "Without Plexi Glass"
    },
    {
      "size": "8 x 12 inches"
    },
    {
      "style": "Paper"
    }
  ],
  "variationtheme": "SIZE_NAME/STYLE_NAME/CUSTOMER_PACKAGE_TYPE",
  "parentasin": "B0CK7WBJH7",
  "parentsku": "Mad 2139-$P"
}
```

