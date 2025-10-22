# Dzgro API Documentation

## Overview

This is the REST API for the Dzgro platform, providing endpoints for managing Amazon seller accounts, marketplaces, analytics, and advertising data.

**Base URL**: `https://api.dzgro.com/v1` (Production)
**Base URL**: `https://dev-api.dzgro.com/v1` (Development)

**Architecture**: AWS Lambda + API Gateway (SAM Framework)
**Database**: MongoDB Atlas (see [DATABASE.md](../database/DATABASE.md))

## Authentication

All API endpoints require JWT Bearer token authentication via AWS Cognito.

```http
Authorization: Bearer {cognito-jwt-token}
```

**Token Flow**:
1. User authenticates via Cognito (login)
2. Receives JWT access token
3. Include token in all API requests
4. Token contains `uid` (user ID) for authorization

## API Versioning

Current Version: **v1**

All endpoints are prefixed with `/api/v1/`

## Common Patterns

### Standard Response Format

**Success Response**:
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

### Pagination

For list endpoints:

**Request**:
```
GET /api/v1/resource?page=1&limit=20
```

**Response**:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

### Filtering

Common query parameters:
- `marketplace` - Filter by marketplace ObjectId
- `startDate` - Filter by date range (ISO 8601)
- `endDate` - Filter by date range (ISO 8601)
- `status` - Filter by status enum

### Sorting

```
GET /api/v1/resource?sortBy=createdAt&order=desc
```

## API Contracts

Detailed API contracts for each feature:

### User & Account Management

- [User Profile](./contracts/user-profile.md) - User account management
- [SPAPI Accounts](./contracts/spapi-accounts.md) - Amazon Seller accounts
- [Advertising Accounts](./contracts/advertising-accounts.md) - Amazon Advertising accounts
- [Marketplaces](./contracts/marketplaces.md) - Marketplace connections

### Products & Inventory

- [Products](./contracts/products.md) - Product catalog management
- [Inventory Health](./contracts/inventory-health.md) - Stock levels and health metrics

### Orders & Fulfillment

- [Orders](./contracts/orders.md) - Order management
- [Order Items](./contracts/order-items.md) - Individual order line items
- [Settlements](./contracts/settlements.md) - Payment settlements from Amazon

### Analytics & Reporting

- [Date Analytics](./contracts/date-analytics.md) - Daily analytics data
- [State Analytics](./contracts/state-analytics.md) - State-wise analytics
- [Performance Periods](./contracts/performance-periods.md) - Period-based performance
- [Traffic Analytics](./contracts/traffic-analytics.md) - Product traffic data

### Advertising

- [Advertising Assets](./contracts/adv-assets.md) - Campaigns, ad groups, keywords
- [Advertising Performance](./contracts/adv-performance.md) - Ad performance metrics
- [Advertising Rules](./contracts/adv-rules.md) - Automation rules

### Payments & Billing

- [Payments](./contracts/payments.md) - Payment management
- [Pricing Plans](./contracts/pricing.md) - Subscription plans
- [Invoices](./contracts/invoices.md) - Invoice generation

## Error Codes

### Standard HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `500` - Internal Server Error

### Application Error Codes

| Code | Description |
|------|-------------|
| `INVALID_PARAMETERS` | Request parameters validation failed |
| `MARKETPLACE_NOT_FOUND` | Marketplace doesn't exist or user doesn't have access |
| `UNAUTHORIZED_MARKETPLACE` | User doesn't own the marketplace |
| `SPAPI_ACCOUNT_NOT_FOUND` | SPAPI account not found |
| `ADV_ACCOUNT_NOT_FOUND` | Advertising account not found |
| `DUPLICATE_MARKETPLACE` | Marketplace already exists |
| `INVALID_DATE_RANGE` | Date range is invalid |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

## Rate Limiting

- **Authenticated requests**: 1000 requests per minute
- **Unauthenticated requests**: 100 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## CORS

Allowed origins:
- `https://app.dzgro.com` (Production)
- `http://localhost:4200` (Development)

## Webhooks

### Amazon SP-API Notifications

Endpoint: `POST /api/v1/webhooks/spapi`

### Razorpay Payment Notifications

Endpoint: `POST /api/v1/webhooks/razorpay`

## Database Reference

All API endpoints interact with MongoDB collections documented in [DATABASE.md](../database/DATABASE.md).

**Key Collections**:
- `users` - User accounts
- `marketplaces` - Marketplace configurations
- `spapi_accounts` - Amazon Seller credentials
- `advertising_accounts` - Amazon Advertising credentials
- `products` - Product catalog
- `orders` - Orders data
- `date_analytics` - Daily analytics
- `adv_performance` - Advertising performance

See [Database Collections](../database/DATABASE.md#collections-by-category) for full list.

## Development

### Local Development

```bash
# Start SAM local API
sam local start-api --port 3000

# API available at
http://localhost:3000/api/v1/...
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_marketplaces.py
```

### Creating New Endpoints

1. Create API contract in `docs/api/contracts/[feature].md` using [TEMPLATE.md](./TEMPLATE.md)
2. Implement backend Lambda function
3. Update `template.yaml` with new API Gateway routes
4. Create/update database helpers in `dzgroshared/db/[collection]/`
5. Write tests
6. Deploy to dev environment

## Deployment

### Development Environment

```bash
sam deploy --config-env dev
```

### Production Environment

```bash
sam deploy --config-env prod
```

## Support

For API issues or questions:
- GitHub Issues: https://github.com/dzgro/sam-app/issues
- Email: support@dzgro.com

---

*Last Updated: 2025-10-21*
*API Version: v1*
