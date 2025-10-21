# health - Structure

## Overview
- **Collection**: `health`
- **Document Count**: 1
- **Average Document Size**: 3781 bytes
- **Total Size**: 3,781 bytes

## Fields

### `_id`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`

### `health`

- **Type**: `dict`

### `health.ahr`

- **Type**: `dict`

### `health.ahr.baseline`

- **Type**: `int`
- **Sample Values**: `1000`

### `health.ahr.score`

- **Type**: `int`
- **Sample Values**: `340`

### `health.ahr.status`

- **Type**: `str`
- **Sample Values**: `GREAT`

### `health.defectRates`

- **Type**: `dict`

### `health.defectRates.afn`

- **Type**: `dict`

### `health.defectRates.afn.days`

- **Type**: `str`
- **Sample Values**: `60days`

### `health.defectRates.afn.description`

- **Type**: `str`
- **Sample Values**: `The Order Defect Rate (ODR) is a performance metric that Amazon uses to rate the seller's customer service standards`

### `health.defectRates.afn.fulfillment`

- **Type**: `str`
- **Sample Values**: `afn`

### `health.defectRates.afn.isAcceptable`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `health.defectRates.afn.items`

- **Type**: `list[]`

### `health.defectRates.afn.items.title`

- **Type**: `str`
- **Sample Values**: `Negative Feedback`

### `health.defectRates.afn.items.value`

- **Type**: `str`
- **Sample Values**: `-`

### `health.defectRates.afn.subtitle`

- **Type**: `str`
- **Sample Values**: `No Orders`

### `health.defectRates.afn.target`

- **Type**: `str`
- **Sample Values**: `<1.0%`

### `health.defectRates.afn.title`

- **Type**: `str`
- **Sample Values**: `Amazon Fulfilled Order Defect Rate`

### `health.defectRates.afn.value`

- **Type**: `str`
- **Sample Values**: `-`

### `health.defectRates.mfn`

- **Type**: `dict`

### `health.defectRates.mfn.days`

- **Type**: `str`
- **Sample Values**: `60days`

### `health.defectRates.mfn.description`

- **Type**: `str`
- **Sample Values**: `The Order Defect Rate (ODR) is a performance metric that Amazon uses to rate the seller's customer service standards`

### `health.defectRates.mfn.fulfillment`

- **Type**: `str`
- **Sample Values**: `mfn`

### `health.defectRates.mfn.isAcceptable`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `health.defectRates.mfn.items`

- **Type**: `list[]`

### `health.defectRates.mfn.items.title`

- **Type**: `str`
- **Sample Values**: `Negative Feedback`

### `health.defectRates.mfn.items.value`

- **Type**: `str`
- **Sample Values**: `2 Orders`

### `health.defectRates.mfn.subtitle`

- **Type**: `str`
- **Sample Values**: `2 of 1936 orders`

### `health.defectRates.mfn.target`

- **Type**: `str`
- **Sample Values**: `<1.0%`

### `health.defectRates.mfn.title`

- **Type**: `str`
- **Sample Values**: `Seller`

### `health.defectRates.mfn.value`

- **Type**: `str`
- **Sample Values**: `0.1%`

### `health.invoiceDefectRate`

- **Type**: `dict`

### `health.invoiceDefectRate.days`

- **Type**: `str`
- **Sample Values**: `7days`

### `health.invoiceDefectRate.description`

- **Type**: `str`
- **Sample Values**: `The Invoice Defect Rate (IDR) for Amazon is the percentage of orders from Amazon Business customers with the invoice not uploaded within one business day after shipment`

### `health.invoiceDefectRate.isAcceptable`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `health.invoiceDefectRate.items`

- **Type**: `list[]`

### `health.invoiceDefectRate.items.title`

- **Type**: `str`
- **Sample Values**: `Invoice Defects`

### `health.invoiceDefectRate.items.value`

- **Type**: `str`
- **Sample Values**: `-`

### `health.invoiceDefectRate.subtitle`

- **Type**: `str`
- **Sample Values**: `No Orders`

### `health.invoiceDefectRate.target`

- **Type**: `str`
- **Sample Values**: `<5.0%`

### `health.invoiceDefectRate.title`

- **Type**: `str`
- **Sample Values**: `Invoice Defect Rate`

### `health.invoiceDefectRate.value`

- **Type**: `str`
- **Sample Values**: `-`

### `health.rateMetrics`

- **Type**: `list[]`

### `health.rateMetrics.days`

- **Type**: `str`
- **Sample Values**: `30 days`

### `health.rateMetrics.desc`

- **Type**: `str`
- **Sample Values**: `Amazon's late shipment rate (LSR) is a metric that measures how many orders a seller ships late. It's calculated by dividing the number of late orders by the total number of orders in a given time period.`

### `health.rateMetrics.isAcceptable`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `health.rateMetrics.subtitle`

- **Type**: `str`
- **Sample Values**: `0 of 834 orders`

### `health.rateMetrics.target`

- **Type**: `str`
- **Sample Values**: `<2.0%`

### `health.rateMetrics.title`

- **Type**: `str`
- **Sample Values**: `Late Shipment Rate`

### `health.rateMetrics.value`

- **Type**: `str`
- **Sample Values**: `0.0%`

### `health.violation`

- **Type**: `dict`

### `health.violation.categories`

- **Type**: `int`
- **Sample Values**: `0`

### `health.violation.isAcceptable`

- **Type**: `bool`
- **Enum Values**: `true`, `false`

### `health.violation.subtitle`

- **Type**: `str`
- **Sample Values**: `Click for Details`

### `health.violation.title`

- **Type**: `str`
- **Sample Values**: `Violations`

### `health.violation.value`

- **Type**: `int`
- **Sample Values**: `0`

### `health.violation.violations`

- **Type**: `list[]`

### `health.violation.violations.name`

- **Type**: `str`
- **Sample Values**: `Listing Policy Violations`

### `health.violation.violations.value`

- **Type**: `int`
- **Sample Values**: `0`

### `marketplace`

- **Type**: `ObjectId`
- **Sample Values**: `6895638c452dc4315750e826`

### `synctoken`

- **Type**: `ObjectId`
- **Sample Values**: `68bfa71ad8a531d44e4b8fef`

### `uid`

- **Type**: `str`
- **Sample Values**: `41e34d1a-6031-70d2-9ff3-d1a704240921`


## Sample Documents

### Sample 1

```json
{
  "_id": "6895638c452dc4315750e826",
  "health": {
    "ahr": {
      "score": 340,
      "status": "GREAT",
      "baseline": 1000
    },
    "defectRates": {
      "afn": {
        "value": "-",
        "target": "<1.0%",
        "subtitle": "No Orders",
        "days": "60days",
        "isAcceptable": true,
        "fulfillment": "afn",
        "title": "Amazon Fulfilled Order Defect Rate",
        "description": "The Order Defect Rate (ODR) is a performance metric that Amazon uses to rate the seller's customer service standards",
        "items": [
          {
            "title": "Negative Feedback",
            "value": "-"
          },
          {
            "title": "A-Z Claims",
            "value": "-"
          },
          {
            "title": "Chargeback Claims",
            "value": "-"
          }
        ]
      },
      "mfn": {
        "value": "0.1%",
        "target": "<1.0%",
        "subtitle": "2 of 1936 orders",
        "days": "60days",
        "isAcceptable": true,
        "fulfillment": "mfn",
        "title": "Seller",
        "description": "The Order Defect Rate (ODR) is a performance metric that Amazon uses to rate the seller's customer service standards",
        "items": [
          {
            "title": "Negative Feedback",
            "value": "2 Orders"
          },
          {
            "title": "A-Z Claims",
            "value": "-"
          },
          {
            "title": "Chargeback Claims",
            "value": "-"
          }
        ]
      }
    },
    "invoiceDefectRate": {
      "value": "-",
      "target": "<5.0%",
      "subtitle": "No Orders",
      "days": "7days",
      "isAcceptable": true,
      "title": "Invoice Defect Rate",
      "description": "The Invoice Defect Rate (IDR) for Amazon is the percentage of orders from Amazon Business customers with the invoice not uploaded within one business day after shipment",
      "items": [
        {
          "title": "Invoice Defects",
          "value": "-"
        },
        {
          "title": "Missing Invoice",
          "value": "-"
        },
        {
          "title": "Late Invoice",
          "value": "-"
        }
      ]
    },
    "rateMetrics": [
      {
        "value": "0.0%",
        "target": "<2.0%",
        "subtitle": "0 of 834 orders",
        "days": "30 days",
        "isAcceptable": true,
        "title": "Late Shipment Rate",
        "desc": "Amazon's late shipment rate (LSR) is a metric that measures how many orders a seller ships late. It's calculated by dividing the number of late orders by the total number of orders in a given time period."
      },
      {
        "value": "0.0%",
        "target": "<2.0%",
        "subtitle": "0 of 865 orders",
        "days": "30 days",
        "isAcceptable": true,
        "title": "Pre-fulfillment Cancel Rate",
        "desc": "A pre-fulfillment cancellation rate (PCR) is the percentage of orders that a seller cancels before they are shipped. It is calculated by dividing the number of cancellations by the total number of orders placed within a given time period. The reason for the cancellation is not considered in the calculation."
      },
      {
        "value": "98.8%",
        "target": ">97.0%",
        "subtitle": "883 of 894 orders",
        "days": "30 days",
        "isAcceptable": true,
        "title": "On Time Delivery Rate",
        "desc": "Your OTDR includes all shipments which are delivered by their Estimated Delivery Date (EDD) represented as a percentage of total tracked shipments. OTDR only applies to seller-fulfilled orders"
      },
      {
        "value": "100.0%",
        "target": ">95.0%",
        "subtitle": "894 of 894 orders",
        "days": "30 days",
        "isAcceptable": true,
        "title": "Valid Tracking Rate",
        "desc": "The Valid Tracking Rate (VTR) measures the percentage of seller-fulfilled orders that have a valid tracking number."
      }
    ],
    "violation": {
      "title": "Violations",
      "subtitle": "Click for Details",
      "categories": 0,
      "isAcceptable": true,
      "value": 0,
      "violations": [
        {
          "name": "Listing Policy Violations",
          "value": 0
        },
        {
          "name": "Product Authenticity Customer Complaints",
          "value": 0
        },
        {
          "name": "Product Condition Customer Complaints",
          "value": 0
        },
        {
          "name": "Product Safety Customer Complaints",
          "value": 0
        },
        {
          "name": "IP Complaints",
          "value": 0
        },
        {
          "name": "Restricted Product Policy Complaints",
          "value": 0
        },
        {
          "name": "Suspected IP Violations",
          "value": 0
        },
        {
          "name": "Food & Safety Issues",
          "value": 0
        },
        {
          "name": "Customer Product Reviews Violations",
          "value": 0
        },
        {
          "name": "Other Policy Violations",
          "value": 0
        },
        {
          "name": "Document Requests",
          "value": 0
        }
      ]
    }
  },
  "marketplace": "6895638c452dc4315750e826",
  "synctoken": "68bfa71ad8a531d44e4b8fef",
  "uid": "41e34d1a-6031-70d2-9ff3-d1a704240921"
}
```

