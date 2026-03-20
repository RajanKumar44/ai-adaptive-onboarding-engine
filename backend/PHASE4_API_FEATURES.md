# Phase 4: Advanced API Features Implementation Guide

## Overview

Phase 4 introduces advanced API features including pagination, filtering, sorting, search, and bulk operations. These features enable more flexible and efficient data retrieval and manipulation while maintaining backward compatibility with existing endpoints.

**Status**: ✅ Complete
**Commit**: (to be added after git commit)
**Duration**: Implementation + Testing

## Table of Contents

1. [Pagination](#pagination)
2. [Filtering & Sorting](#filtering--sorting)
3. [Advanced Search](#advanced-search)
4. [Bulk Operations](#bulk-operations)
5. [API Examples](#api-examples)
6. [Configuration](#configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Pagination

### Overview

Pagination allows retrieving large datasets in manageable chunks using limit/offset parameters.

### Pagination Models

#### Standard Pagination (Limit/Offset)

```python
# Query Parameters
- skip: int (default=0, ge=0) - Records to skip
- limit: int (default=10, ge=1, le=100) - Records to return per page
```

#### Response Format

```json
{
  "data": [...],           // Array of items
  "total": 1500,          // Total items available
  "skip": 0,              // Items skipped
  "limit": 10,            // Items returned
  "page": 1,              // Current page (1-indexed)
  "pages": 150,           // Total pages
  "has_next": true,       // Whether next page exists
  "has_prev": false       // Whether previous page exists
}
```

### Pagination Presets

Different entity types use different default and maximum page sizes:

| Entity Type | Default | Maximum |
|---|---|---|
| Small (Users, Roles) | 10 | 50 |
| Medium (Analyses, Results) | 25 | 100 |
| Large (Logs, Events) | 50 | 500 |
| Very Large (Audit Logs) | 100 | 1000 |

### Usage Examples

#### Get First 10 Users
```http
GET /api/v1/admin/users?skip=0&limit=10
```

#### Get Second Page (items 10-20)
```http
GET /api/v1/admin/users?skip=10&limit=10
```

#### Get Maximum Allowed (100 items)
```http
GET /api/v1/users/1/analyses?skip=0&limit=100
```

#### Calculate Pages
```python
# Frontend pagination calculation
current_page = (skip // limit) + 1
total_pages = ceil(total / limit)
next_skip = skip + limit
```

---

## Filtering & Sorting

### Overview

Advanced filtering allows querying data with multiple conditions. Sorting enables result ordering by one or more fields.

### Filter Operators

```
eq       - Equals
ne       - Not equals
gt       - Greater than
gte      - Greater than or equal
lt       - Less than
lte      - Less than or equal
like     - String contains (case-insensitive)
in       - Value in list
between  - Between two values
is_null  - Is null / is not null
```

### Sorting

#### Query Parameters
```
sort_by: str     - Field to sort by (e.g., "created_at", "name")
sort_order: str  - "asc" or "desc" (default: "desc")
```

#### Multiple Sort Fields
```
Max 3 sort fields per query for performance
```

### Supported Fields by Endpoint

#### Users List (`GET /api/v1/admin/users`)
**Sortable Fields**: `id`, `email`, `name`, `role`, `is_active`, `created_at`, `updated_at`

**Filterable Fields**:
- `filter_role`: admin | user | guest
- `filter_active`: true | false

#### Analyses List (`GET /api/v1/users/{user_id}/analyses`)
**Sortable Fields**: `id`, `created_at`, `updated_at`

**Filterable Fields**: None (uses search instead)

### Usage Examples

#### Sort by Creation Date (Newest First)
```http
GET /api/v1/admin/users?skip=0&limit=10&sort_by=created_at&sort_order=desc
```

#### Sort by Name (A-Z)
```http
GET /api/v1/admin/users?skip=0&limit=10&sort_by=name&sort_order=asc
```

#### Filter by Role Admin Only
```http
GET /api/v1/admin/users?filter_role=admin&skip=0&limit=10
```

#### Filter Active Users Only
```http
GET /api/v1/admin/users?filter_active=true&skip=0&limit=10
```

#### Combine Sorting and Filtering
```http
GET /api/v1/admin/users?filter_role=user&filter_active=true&sort_by=created_at&sort_order=desc&skip=0&limit=10
```

---

## Advanced Search

### Overview

Full-text search across text fields enables quick discovery of records by keyword matching.

### Search Modes

```
simple   - Basic substring matching (default)
phrase   - Exact phrase matching
boolean  - Boolean operators (AND, OR, NOT)
fuzzy    - Approximate matching (future)
```

### Supported Fields by Endpoint

#### Users (`GET /api/v1/admin/users`)
- `name`
- `email`

#### Analyses (`GET /api/v1/users/{user_id}/analyses`)
- `resume_text`
- `jd_text`

### Search Features

| Feature | Support | Example |
|---|---|---|
| Case-insensitive | ✅ | search=Python matches python |
| Partial matching | ✅ | search=Pyt matches Python |
| Special characters | ❌ | Automatically stripped |
| Minimum length | 2 | search=a rejected, search=ab accepted |
| Highlighting | ✅ | Wrap matches in `<mark>` tag |

### Usage Examples

#### Find Users by Name or Email
```http
GET /api/v1/admin/users?search=john&skip=0&limit=10
```

#### Find Analyses with Specific Skill
```http
GET /api/v1/users/1/analyses?search=python&skip=0&limit=10
```

#### Combine Search with Sorting
```http
GET /api/v1/admin/users?search=john&sort_by=created_at&sort_order=desc&skip=0&limit=10
```

#### Combine Search, Filter, and Sort
```http
GET /api/v1/admin/users?search=john&filter_role=admin&sort_by=email&skip=0&limit=10
```

---

## Bulk Operations

### Overview

Bulk operations enable creating, updating, or deleting multiple records in a single atomic request.

### Bulk Operation Types

```
create  - Create multiple new records
update  - Update existing records (requires id)
delete  - Delete multiple records
upsert  - Create or update (create if id missing, update if exists)
```

### Request Format

```json
{
  "operation": "create|update|delete|upsert",
  "items": [
    { /* item 1 */ },
    { /* item 2 */ }
  ],
  "atomic": true    // All-or-nothing mode
}
```

### Response Format

```json
{
  "operation": "create",
  "total_items": 10,
  "successful_items": 10,
  "failed_items": 0,
  "items": [
    {
      "index": 0,
      "status": "success",
      "success": true,
      "data": {...},
      "error": null
    }
  ],
  "duration_ms": 245.3,
  "success_rate": 1.0,
  "started_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:30:00.245",
  "errors_summary": []
}
```

### Endpoints

#### User Bulk Operations (Admin Only)

```
POST /api/v1/bulk/users/create     - Create multiple users
POST /api/v1/bulk/users/update     - Update multiple users
POST /api/v1/bulk/users/delete     - Delete user by IDs
```

#### Analysis Bulk Operations (User/Admin)

```
POST /api/v1/bulk/analyses/create  - Create multiple analyses
POST /api/v1/bulk/analyses/update  - Update multiple analyses
POST /api/v1/bulk/analyses/delete  - Delete analyses by IDs
POST /api/v1/bulk/analyses/upsert  - Create or update analyses
```

### Atomic Mode

| Mode | Behavior | Use Case |
|---|---|---|
| `atomic=true` | All succeed or all fail | Critical data migrations |
| `atomic=false` | Partial success allowed | Data imports with errors |

### Rate Limiting

Bulk operations have strict rate limiting: **5 requests per minute**

### Constraints

- Maximum 100 items per request
- Maximum 1000 items per atomic transaction
- Request timeout: 30 seconds

### Usage Examples

#### Bulk Create Users
```http
POST /api/v1/bulk/users/create
Content-Type: application/json

{
  "operation": "create",
  "items": [
    {
      "email": "user1@example.com",
      "name": "User One",
      "password_hash": "...",
      "role": "user"
    },
    {
      "email": "user2@example.com",
      "name": "User Two",
      "password_hash": "...",
      "role": "user"
    }
  ],
  "atomic": true
}
```

#### Bulk Update User Roles
```http
POST /api/v1/bulk/users/update
Content-Type: application/json

{
  "operation": "update",
  "items": [
    {"id": 1, "role": "admin"},
    {"id": 2, "role": "user"}
  ],
  "atomic": true
}
```

#### Bulk Delete Users
```http
POST /api/v1/bulk/users/delete?atomic=true
Content-Type: application/json

[1, 2, 3, 4, 5]
```

#### Bulk Upsert Analyses
```http
POST /api/v1/bulk/analyses/upsert
Content-Type: application/json

{
  "operation": "upsert",
  "items": [
    {
      "id": 1,
      "learning_path": {...}
    },
    {
      "user_id": 1,
      "resume_text": "...",
      "jd_text": "..."
    }
  ],
  "atomic": false
}
```

---

## API Examples

### Example 1: Search and Paginate Users

```bash
# Search for "john" in names/emails, sorted by newest, paginate
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer <token>" \
  -G \
  -d search=john \
  -d sort_by=created_at \
  -d sort_order=desc \
  -d skip=0 \
  -d limit=20
```

### Example 2: Filter and Sort

```bash
# Get active admin users, sorted by email
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer <token>" \
  -G \
  -d filter_role=admin \
  -d filter_active=true \
  -d sort_by=email \
  -d sort_order=asc \
  -d skip=0 \
  -d limit=50
```

### Example 3: Bulk Create and Handle Errors

```bash
curl -X POST "http://localhost:8000/api/v1/bulk/users/create" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "create",
    "items": [
      {"email": "user1@example.com", "name": "User 1", "password_hash": "..."},
      {"email": "user2@example.com", "name": "User 2", "password_hash": "..."}
    ],
    "atomic": false
  }'
```

### Example 4: Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Authorization": f"Bearer {access_token}"}

# Pagination with search and sort
response = requests.get(
    f"{BASE_URL}/admin/users",
    headers=HEADERS,
    params={
        "search": "john",
        "sort_by": "created_at",
        "sort_order": "desc",
        "skip": 0,
        "limit": 10
    }
)

data = response.json()
print(f"Found {data['total']} users")
print(f"Page {data['page']} of {data['pages']}")

# Bulk operations
bulk_data = {
    "operation": "create",
    "items": [
        {"email": "new1@example.com", "name": "New User 1", "password_hash": "..."},
        {"email": "new2@example.com", "name": "New User 2", "password_hash": "..."}
    ],
    "atomic": True
}

response = requests.post(
    f"{BASE_URL}/bulk/users/create",
    headers=HEADERS,
    json=bulk_data
)

result = response.json()
print(f"Success: {result['successful_items']}/{result['total_items']}")
```

---

## Configuration

### Environment Variables

```bash
# Pagination
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100

# Filtering
MAX_FILTERS_PER_QUERY=10
DEFAULT_SORT_ORDER=desc
MAX_SORT_FIELDS=3

# Search
MIN_SEARCH_LENGTH=2
MAX_SEARCH_LENGTH=500
SEARCH_TIMEOUT_SECONDS=5.0

# Bulk Operations
BULK_OPERATION_BATCH_SIZE=100
BULK_OPERATION_MAX_ITEMS=1000
BULK_OPERATION_ATOMIC_DEFAULT=true
```

### Configuration in Code

```python
from app.core.config import get_settings

settings = get_settings()

# Access pagination settings
default_size = settings.DEFAULT_PAGE_SIZE
max_size = settings.MAX_PAGE_SIZE

# Access filtering settings
max_filters = settings.MAX_FILTERS_PER_QUERY
default_sort = settings.DEFAULT_SORT_ORDER

# Access search settings
min_length = settings.MIN_SEARCH_LENGTH
timeout = settings.SEARCH_TIMEOUT_SECONDS

# Access bulk operation settings
batch_size = settings.BULK_OPERATION_BATCH_SIZE
max_items = settings.BULK_OPERATION_MAX_ITEMS
```

---

## Best Practices

### 1. Pagination Best Practices

```python
# ✅ GOOD: Use reasonable page sizes
params = {"skip": 0, "limit": 20}

# ❌ BAD: Requesting everything at once
params = {"skip": 0, "limit": 100000}

# ✅ GOOD: Check has_next before requesting more
if response_data["has_next"]:
    next_page = get_next_page()

# ❌ BAD: Assuming there are more pages
next_page = get_page(skip + limit)
```

### 2. Search Best Practices

```python
# ✅ GOOD: Meaningful search terms
search="python developer"

# ❌ BAD: Single character searches (rejected)
search="p"

# ✅ GOOD: Handle empty results gracefully
if len(results) == 0:
    return "No results found"

# ✅ GOOD: Combine search with filters for narrow results
GET /users?search=john&filter_role=admin
```

### 3. Filtering Best Practices

```python
# ✅ GOOD: Specific filters
filter_role=admin&filter_active=true

# ❌ BAD: Too many filter conditions (>10)
filter_active=true&filter_created_after=2024&...

# ✅ GOOD: Use filters for categorical data
filter_role, filter_status, filter_active

# ❌ BAD: Use filters for ranges (use search instead)
# Use filter_created_between instead of multiple filters
```

### 4. Bulk Operation Best Practices

```python
# ✅ GOOD: Reasonable batch sizes
items = [1, 2, 3, ..., 50]  # 50 items

# ❌ BAD: Too large batches
items = [1, 2, 3, ..., 10000]  # Will fail

# ✅ GOOD: Use atomic=false for imports with expected errors
"atomic": false

# ✅ GOOD: Use atomic=true for critical operations
"atomic": true

# ✅ GOOD: Check success_rate in response
if result["success_rate"] < 0.9:
    log_errors(result["errors_summary"])
```

### 5. Performance Best Practices

```python
# ✅ GOOD: Combine filters instead of fetching all
GET /users?filter_role=admin&filter_active=true

# ❌ BAD: Fetch all then filter in application
results = get_all_users()  # 100,000 users!
filtered = [u for u in results if u.role == "admin"]

# ✅ GOOD: Use pagination for large results
while has_next:
    page = get_next_page()
    process(page)

# ✅ GOOD: Use search for text matching
GET /users?search=pattern

# ❌ BAD: Don't use like filter for every field
filter_name=john&filter_email=john&...
```

---

## Troubleshooting

### Issue: Pagination Limit Exceeded

**Problem**: Request returns "Limit must be less than or equal to 100"

**Solution**:
```python
# Use maximum allowed limit
limit = min(requested_limit, 100)

# Or use preset by entity type
if entity_type == "user":
    limit = min(requested_limit, 50)  # Small preset
elif entity_type == "analysis":
    limit = min(requested_limit, 100)  # Medium preset
```

### Issue: Search Returns No Results

**Problem**: Search returns empty even though records exist

**Solution**:
```python
# Check minimum length
search_term = "ab"  # ✅ Meets minimum (2 chars)
search_term = "a"   # ❌ Fails minimum length

# Check case-insensitivity
search="Python"  # Matches "python" ✅

# Check partial matching
search="pyt"     # Matches "python" ✅

# Check special characters stripped
search="john@"   # @ removed, searches for "john" ✅
```

### Issue: Filter Returns No Results

**Problem**: Invalid filter syntax or no matching records

**Solution**:
```python
# Validate filter operator
filter_role=admin        # ✅ Valid role value
filter_role=superuser    # ❌ Invalid role value

# Check field exists
sort_by=created_at       # ✅ Valid sortable field
sort_by=favorite_color   # ❌ Field doesn't exist

# Use correct boolean format
filter_active=true       # ✅ Boolean string
filter_active=1          # ❌ Won't work
```

### Issue: Bulk Operation Rate Limited

**Problem**: "429 Too Many Requests" on bulk operations

**Solution**:
```python
# Rate limit: 5 requests per minute
# Wait before retrying
time.sleep(12)  # Wait 12 seconds

# Reduce request frequency
def batch_upsert(items, delay=15):
    for batch in chunks(items, 100):
        upsert(batch)
        time.sleep(delay)
```

### Issue: Bulk Operation Timeout

**Problem**: Request times out with large batch

**Solution**:
```python
# Reduce batch size
# Maximum recommended: 100 items per request
items = items[:100]

# Use async processing for larger batches
async_process_bulk_items(items)

# Check BULK_OPERATION_BATCH_SIZE setting
# May need to reduce for slower databases
```

### Issue: Authorization Error on Bulk Delete

**Problem**: 403 Forbidden when trying to delete analyses

**Solution**:
```python
# Users can only delete their own analyses
# Admins can delete any analyses

# For regular users: Filter by user_id first
my_analyses = get_user_analyses(current_user.id)
ids_to_delete = [a.id for a in my_analyses]
delete_analyses(ids_to_delete)

# For admins: Can delete any analysis
all_ids = [1, 2, 3, 4, 5]
delete_analyses(all_ids)
```

---

## Features Summary

| Feature | Status | Details |
|---|---|---|
| Pagination | ✅ Complete | Limit/offset with metadata |
| Sorting | ✅ Complete | Multiple fields, asc/desc |
| Filtering | ✅ Complete | Multiple operators, various fields |
| Search | ✅ Complete | Full-text, highlighting |
| Bulk Create | ✅ Complete | Atomic + partial modes |
| Bulk Update | ✅ Complete | By ID, atomic + partial |
| Bulk Delete | ✅ Complete | By ID array, atomic + partial |
| Bulk Upsert | ✅ Complete | Create or update by ID |
| Rate Limiting | ✅ Complete | 5 requests/min for bulk ops |
| Error Handling | ✅ Complete | Per-item status tracking |

---

## Next Steps

1. **Test all endpoints** in API documentation (/api/v1/docs)
2. **Review examples** above for your use case
3. **Configure settings** in .env for your needs
4. **Integrate into** frontend applications
5. **Monitor performance** via Prometheus metrics
6. **Log issues** for tracking and debugging

---

## Support

For issues, questions, or feature requests:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [Best Practices](#best-practices) 
3. Check application logs in `/logs` directory
4. Review Sentry error tracking if configured
5. Check Prometheus metrics at `/api/v1/metrics/prometheus`

---

**Last Updated**: Phase 4 Implementation
**Version**: 1.0.0
**Compatibility**: FastAPI 0.109+, SQLAlchemy 2.0+, Python 3.9+
