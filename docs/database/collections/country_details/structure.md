# country_details - Structure

## Overview
- **Collection**: `country_details`
- **Document Count**: 22
- **Average Document Size**: 838 bytes
- **Total Size**: 18,451 bytes

## Fields

### `_id`

- **Type**: `str`
- **Sample Values**: `BR`, `US`, `NL`

### `ad_auth_url`

- **Type**: `str`
- **Sample Values**: `https://www.amazon.com/ap/oa`, `https://www.amazon.com/ap/oa`, `https://eu.account.amazon.com/ap/oa`

### `ad_url`

- **Type**: `str`
- **Sample Values**: `https://advertising-api.amazon.com`, `https://advertising-api.amazon.com`, `https://advertising-api-eu.amazon.com`

### `auth_url`

- **Type**: `str`
- **Sample Values**: `https://api.amazon.com/auth/o2/token`, `https://api.amazon.com/auth/o2/token`, `https://api.amazon.co.uk/auth/o2/token`

### `bids`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.image`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.image.cpc_image`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.image.cpc_image.max`

- **Type**: `int`
- **Sample Values**: `200`, `49`, `39`

### `bids.SPONSORED_BRANDS.image.cpc_image.min`

- **Type**: `int | float`

### `bids.SPONSORED_BRANDS.image.vcpm_image_bis`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.image.vcpm_image_bis.max`

- **Type**: `int`
- **Sample Values**: `8000`, `5000`, `1560`

### `bids.SPONSORED_BRANDS.image.vcpm_image_bis.min`

- **Type**: `int | float`

### `bids.SPONSORED_BRANDS.image.vcpm_image_ntb`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.image.vcpm_image_ntb.max`

- **Type**: `int`
- **Sample Values**: `8000`, `5000`, `1560`

### `bids.SPONSORED_BRANDS.video`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.video.cpc_video`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.video.cpc_video.max`

- **Type**: `int`
- **Sample Values**: `25000`, `49`, `39`

### `bids.SPONSORED_BRANDS.video.cpc_video.min`

- **Type**: `int | float`

### `bids.SPONSORED_BRANDS.video.vcpm_video_bis`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.video.vcpm_video_bis.max`

- **Type**: `int`
- **Sample Values**: `8000`, `5000`, `1560`

### `bids.SPONSORED_BRANDS.video.vcpm_video_bis.min`

- **Type**: `int | float`

### `bids.SPONSORED_BRANDS.video.vcpm_video_ntb`

- **Type**: `dict`

### `bids.SPONSORED_BRANDS.video.vcpm_video_ntb.max`

- **Type**: `int`
- **Sample Values**: `8000`, `5000`, `1560`

### `bids.SPONSORED_BRANDS.video.vcpm_video_ntb.min`

- **Type**: `int | float`

### `bids.SPONSORED_DISPLAY`

- **Type**: `dict`

### `bids.SPONSORED_DISPLAY.cpc`

- **Type**: `dict`

### `bids.SPONSORED_DISPLAY.cpc.max`

- **Type**: `int`
- **Sample Values**: `3700`, `1000`, `1000`

### `bids.SPONSORED_DISPLAY.cpc.min`

- **Type**: `int | float`

### `bids.SPONSORED_DISPLAY.vcpm`

- **Type**: `dict`

### `bids.SPONSORED_DISPLAY.vcpm.max`

- **Type**: `int`
- **Sample Values**: `3700`, `1000`, `1000`

### `bids.SPONSORED_DISPLAY.vcpm.min`

- **Type**: `int | float`

### `bids.SPONSORED_PRODUCTS`

- **Type**: `dict`

### `bids.SPONSORED_PRODUCTS.max`

- **Type**: `int | float`

### `bids.SPONSORED_PRODUCTS.min`

- **Type**: `int | float`

### `country`

- **Type**: `str`
- **Sample Values**: `Brazil`, `USA`, `Netherlands`

### `currencyCode`

- **Type**: `str`
- **Sample Values**: `BRL`, `USD`, `EUR`

### `marketplaceId`

- **Type**: `str`
- **Sample Values**: `A2Q3Y263D00KWC`, `ATVPDKIKX0DER`, `A1805IZSGTT6HS`

### `region`

- **Type**: `str`
- **Sample Values**: `NA`, `NA`, `EU`

### `regionName`

- **Type**: `str`
- **Sample Values**: `North America`, `North America`, `Europe`

### `spapi_auth_url`

- **Type**: `str`
- **Sample Values**: `https://sellercentral.amazon.br`, `https://sellercentral.amazon.com`, `https://sellercentral.amazon.nl`

### `spapi_url`

- **Type**: `str`
- **Sample Values**: `https://sellingpartnerapi-na.amazon.com`, `https://sellingpartnerapi-na.amazon.com`, `https://sellingpartnerapi-eu.amazon.com`

### `timezone`

- **Type**: `str`
- **Sample Values**: `America/Sao_Paulo`, `America/Toronto`, `Europe/Amsterdam`


## Sample Documents

### Sample 1

```json
{
  "_id": "BR",
  "currencyCode": "BRL",
  "country": "Brazil",
  "marketplaceId": "A2Q3Y263D00KWC",
  "region": "NA",
  "regionName": "North America",
  "timezone": "America/Sao_Paulo",
  "auth_url": "https://api.amazon.com/auth/o2/token",
  "ad_url": "https://advertising-api.amazon.com",
  "ad_auth_url": "https://www.amazon.com/ap/oa",
  "spapi_url": "https://sellingpartnerapi-na.amazon.com",
  "spapi_auth_url": "https://sellercentral.amazon.br",
  "bids": {
    "SPONSORED_PRODUCTS": {
      "min": 0.07,
      "max": 3700
    },
    "SPONSORED_DISPLAY": {
      "cpc": {
        "min": 0.07,
        "max": 3700
      },
      "vcpm": {
        "min": 2,
        "max": 3700
      }
    },
    "SPONSORED_BRANDS": {
      "image": {
        "cpc_image": {
          "min": 0.53,
          "max": 200
        },
        "vcpm_image_bis": {
          "min": 37,
          "max": 8000
        },
        "vcpm_image_ntb": {
          "max": 8000
        }
      },
      "video": {
        "cpc_video": {
          "min": 0.8,
          "max": 25000
        },
        "vcpm_video_bis": {
          "min": 53,
          "max": 8000
        },
        "vcpm_video_ntb": {
          "min": 10,
          "max": 8000
        }
      }
    }
  }
}
```

### Sample 2

```json
{
  "_id": "US",
  "currencyCode": "USD",
  "country": "USA",
  "marketplaceId": "ATVPDKIKX0DER",
  "region": "NA",
  "regionName": "North America",
  "timezone": "America/Toronto",
  "auth_url": "https://api.amazon.com/auth/o2/token",
  "ad_url": "https://advertising-api.amazon.com",
  "ad_auth_url": "https://www.amazon.com/ap/oa",
  "spapi_url": "https://sellingpartnerapi-na.amazon.com",
  "spapi_auth_url": "https://sellercentral.amazon.com",
  "bids": {
    "SPONSORED_PRODUCTS": {
      "min": 0.02,
      "max": 1000
    },
    "SPONSORED_DISPLAY": {
      "cpc": {
        "min": 0.02,
        "max": 1000
      },
      "vcpm": {
        "min": 1,
        "max": 1000
      }
    },
    "SPONSORED_BRANDS": {
      "image": {
        "cpc_image": {
          "min": 0.1,
          "max": 49
        },
        "vcpm_image_bis": {
          "min": 8,
          "max": 5000
        },
        "vcpm_image_ntb": {
          "max": 5000
        }
      },
      "video": {
        "cpc_video": {
          "min": 0.25,
          "max": 49
        },
        "vcpm_video_bis": {
          "min": 12,
          "max": 5000
        },
        "vcpm_video_ntb": {
          "min": 4,
          "max": 5000
        }
      }
    }
  }
}
```

