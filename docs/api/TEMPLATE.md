# [Feature Name] API Contract

## Overview

**Feature**: [Brief description of what this feature does]
**Version**: 1.0
**Created**: [Date]
**Status**: Draft | In Development | Implemented

## Endpoints

### GET /api/v1/[resource]

**Purpose**: Retrieve [resource] data

**Authentication**: Required (JWT Bearer Token)

**Request**:
- **Headers**:
  ```
  Authorization: Bearer {token}
  ```
- **Query Parameters**:
  ```typescript
  {
    marketplace?: string;      // ObjectId of marketplace
    startDate?: string;         // ISO 8601 date
    endDate?: string;           // ISO 8601 date
    page?: number;              // Default: 1
    limit?: number;             // Default: 20, Max: 100
  }
  ```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "_id": "string",
      "field1": "value",
      "field2": 123,
      "createdAt": "2025-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

**Error Responses**:
- **400 Bad Request**: Invalid parameters
  ```json
  {
    "success": false,
    "error": {
      "code": "INVALID_PARAMETERS",
      "message": "Invalid date format",
      "details": { "field": "startDate" }
    }
  }
  ```
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: User doesn't have access to marketplace
- **404 Not Found**: Resource not found

---

### POST /api/v1/[resource]

**Purpose**: Create a new [resource]

**Authentication**: Required (JWT Bearer Token)

**Request**:
- **Headers**:
  ```
  Authorization: Bearer {token}
  Content-Type: application/json
  ```
- **Body**:
  ```json
  {
    "field1": "required string",
    "field2": 123,
    "marketplace": "ObjectId"
  }
  ```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "_id": "newly-created-id",
    "field1": "value",
    "field2": 123,
    "createdAt": "2025-01-01T00:00:00Z"
  }
}
```

**Error Responses**:
- **400 Bad Request**: Validation errors
- **401 Unauthorized**: Missing or invalid token
- **409 Conflict**: Resource already exists

---

### PUT /api/v1/[resource]/:id

**Purpose**: Update an existing [resource]

**Authentication**: Required (JWT Bearer Token)

**Request**:
- **Path Parameters**: `id` (ObjectId)
- **Body**: Same as POST (all fields optional)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "_id": "id",
    "field1": "updated value",
    "updatedAt": "2025-01-01T00:00:00Z"
  }
}
```

**Error Responses**:
- **400 Bad Request**: Validation errors
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: User doesn't own resource
- **404 Not Found**: Resource not found

---

### DELETE /api/v1/[resource]/:id

**Purpose**: Delete a [resource]

**Authentication**: Required (JWT Bearer Token)

**Request**:
- **Path Parameters**: `id` (ObjectId)

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Resource deleted successfully"
}
```

**Error Responses**:
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: User doesn't own resource
- **404 Not Found**: Resource not found

---

## Data Models

### [Resource] Model

Based on `[collection_name]` collection in DATABASE.md

```typescript
interface Resource {
  _id: ObjectId;
  marketplace: ObjectId;        // Reference to marketplaces collection
  uid: string;                  // User ID from Cognito
  field1: string;
  field2: number;
  status: 'Active' | 'Inactive';
  createdAt: Date;
  updatedAt: Date;
}
```

**Relationships**:
- `marketplace` → References `marketplaces._id`
- `uid` → References `users._id`

See: `docs/database/collections/[collection_name]/`

---

## Business Logic

### Validation Rules

1. **Field1**: Required, min 3 chars, max 100 chars
2. **Field2**: Required, must be positive integer
3. **Marketplace**: Must be owned by authenticated user
4. **Status**: Can only transition from Active → Inactive (not reverse)

### Access Control

- Users can only access resources for marketplaces they own
- Check `marketplaces.uid === authenticatedUser.uid`

### Database Operations

1. **On Create**:
   - Validate user owns marketplace
   - Set `createdAt` timestamp
   - Set `uid` from authenticated user

2. **On Update**:
   - Validate user owns resource
   - Update `updatedAt` timestamp
   - Cannot change `uid` or `marketplace`

3. **On Delete**:
   - Soft delete (set `status: 'Deleted'`)
   - Or hard delete if no dependent data

---

## Implementation Notes

### Backend (SAM/Lambda)

**File Structure**:
```
api/src/api/routers/
  [resource]/
    __init__.py
    controller.py        # API handlers
    validators.py        # Request validation

dzgroshared/src/dzgroshared/db/
  [collection]/
    controller.py        # Database operations
    model.py            # Pydantic models
```

**Database Helper**:
- Use existing `DbClient.[collection]` helper
- Leverage existing indexes (see indexes.md)

### Frontend (Angular)

**File Structure**:
```
src/app/
  features/[feature]/
    services/
      [resource].service.ts
    models/
      [resource].model.ts
    components/
      [resource]-list/
      [resource]-detail/
      [resource]-form/
```

**API Service**:
```typescript
@Injectable({ providedIn: 'root' })
export class ResourceService {
  private apiUrl = '/api/v1/resource';

  getAll(params: QueryParams): Observable<ApiResponse<Resource[]>> {
    return this.http.get<ApiResponse<Resource[]>>(this.apiUrl, { params });
  }
}
```

---

## Testing

### Backend Tests

```python
# Test GET endpoint
def test_get_resources_success():
    # Setup: Create test data
    # Execute: Call endpoint
    # Assert: Status 200, correct data returned

def test_get_resources_unauthorized():
    # Execute: Call without token
    # Assert: Status 401
```

### Frontend Tests

```typescript
describe('ResourceService', () => {
  it('should fetch resources successfully', () => {
    // Arrange, Act, Assert
  });
});
```

---

## Migration Notes

**Database Changes**: None (using existing collection)

**Breaking Changes**: None

**Deprecations**: None

---

## Related Documentation

- Database: `docs/database/DATABASE.md`
- Collection: `docs/database/collections/[collection_name]/`
- Related APIs: [List related API contracts]

---

## Changelog

### Version 1.0 (YYYY-MM-DD)
- Initial API design
- Defined all CRUD endpoints
- Documented data models and relationships
