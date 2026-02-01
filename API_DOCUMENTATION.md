# Personal Development App - API Documentation

## Overview

Complete REST API for habit tracking and personal development. Built with Django REST Framework, featuring JWT authentication and comprehensive endpoint coverage.

## Getting Started

### Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://api.personaldevelopment.app`

### Interactive Documentation

- **Swagger UI**: `/api/docs/` - Interactive API explorer with "Try It Out" functionality
- **ReDoc**: `/api/redoc/` - Clean, readable API documentation
- **OpenAPI Schema**: `/api/schema/` - Machine-readable API specification (JSON)

## Authentication

All endpoints (except registration) require **JWT Bearer Token** authentication.

### Getting a Token

**Register a new user:**
```http
POST /api/auth/auth/signup/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using the Token

Include the access token in all subsequent requests:
```http
Authorization: Bearer <access_token>
```

### Refresh Token

When access token expires, refresh it:
```http
POST /api/auth/auth/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}
```

---

## API Endpoints

### Authentication Endpoints

#### Register
```http
POST /api/auth/auth/signup/
```
- **Description**: Create new user account
- **Auth**: Not required
- **Request Body**: Username, email, password, password confirmation
- **Response**: User object + JWT tokens (201)

#### Login
```http
POST /api/auth/auth/login/
```
- **Description**: Authenticate and receive tokens
- **Auth**: Not required
- **Request Body**: Username, password
- **Response**: Access and refresh tokens (200)

#### Refresh Token
```http
POST /api/auth/auth/refresh/
```
- **Description**: Generate new access token using refresh token
- **Auth**: Not required
- **Request Body**: Refresh token
- **Response**: New access token (200)

#### Logout
```http
POST /api/auth/auth/logout/
```
- **Description**: Blacklist refresh token (invalidate session)
- **Auth**: Required
- **Request Body**: Refresh token
- **Response**: Success message (205)

#### Get Profile
```http
GET /api/auth/auth/profile/
```
- **Description**: Get current authenticated user's profile
- **Auth**: Required
- **Response**: User object (200)

---

### Habit Endpoints

#### List Habits
```http
GET /api/habits/
```
- **Description**: Get all habits for current user
- **Auth**: Required
- **Query Parameters**:
  - `page`: Pagination page number (default: 1)
  - `page_size`: Items per page (default: 20)
- **Response**: Paginated list of habits with minimal info (200)

#### Create Habit
```http
POST /api/habits/
```
- **Description**: Create a new habit
- **Auth**: Required
- **Request Body**:
  ```json
  {
    "name": "Morning Meditation",
    "description": "10 minutes daily mindfulness",
    "category": "health",
    "frequency": "daily",
    "goal_count": 1,
    "start_date": "2026-02-01"
  }
  ```
- **Categories**: `health`, `productivity`, `finance`, `learning`, `relationships`, `other`
- **Frequencies**: `daily`, `weekly`, `monthly`
- **Response**: Created habit object (201)

#### Get Habit Details
```http
GET /api/habits/{id}/
```
- **Description**: Get detailed habit info including logs and stats
- **Auth**: Required
- **Response**: Habit object with logs array and calculated stats (200)

#### Update Habit
```http
PATCH /api/habits/{id}/
```
- **Description**: Update habit fields
- **Auth**: Required (must own habit)
- **Request Body**: Any subset of habit fields
- **Response**: Updated habit object (200)

#### Delete Habit
```http
DELETE /api/habits/{id}/
```
- **Description**: Delete a habit and all its logs
- **Auth**: Required (must own habit)
- **Response**: No content (204)

---

### Habit Logging Endpoints

#### Log Habit Completion
```http
POST /api/habits/{id}/log/
```
- **Description**: Log a habit completion for a specific date
- **Auth**: Required (must own habit)
- **Request Body**:
  ```json
  {
    "date": "2026-02-01",
    "completed": true,
    "notes": "Great session today!"
  }
  ```
- **Constraints**: Only one log per habit per day (unique constraint)
- **Response**: Created log object (201)
- **Error**: 400 if log already exists for that day

#### Get Habit Statistics
```http
GET /api/habits/{id}/stats/
```
- **Description**: Get habit statistics (streaks, completion rate)
- **Auth**: Required (must own habit)
- **Response**:
  ```json
  {
    "current_streak": 5,
    "longest_streak": 10,
    "completion_rate": 0.75,
    "total_logs": 20,
    "completed_logs": 15
  }
  ```

---

### Analytics Endpoints

#### Overview Analytics
```http
GET /api/habits/analytics/overview/
```
- **Description**: Get high-level analytics summary for current user
- **Auth**: Required
- **Response**:
  ```json
  {
    "total_habits": 6,
    "active_habits": 5,
    "completion_rate": 84,
    "current_streak": 7,
    "longest_streak": 21,
    "total_completions": 125,
    "category_breakdown": [
      {
        "category": "health",
        "category_label": "Health",
        "habit_count": 2,
        "total_completions": 45
      }
    ]
  }
  ```

#### Weekly Analytics
```http
GET /api/habits/analytics/weekly/
```
- **Description**: Get last 7 days completion statistics
- **Auth**: Required
- **Response**:
  ```json
  {
    "daily_data": [
      {
        "date": "2026-01-27",
        "completions": 3,
        "completion_rate": 60
      }
    ]
  }
  ```

#### Monthly Analytics
```http
GET /api/habits/analytics/monthly/
```
- **Description**: Get current month statistics
- **Auth**: Required
- **Response**:
  ```json
  {
    "year": 2026,
    "month": 2,
    "total_habits": 6,
    "total_completions": 52,
    "completion_rate": 78
  }
  ```

---

### Export Endpoints

#### Export CSV
```http
GET /api/habits/export/csv/
```
- **Description**: Download all habits and logs as CSV
- **Auth**: Required
- **Response**: CSV file download
- **Headers**:
  - `Content-Type: text/csv`
  - `Content-Disposition: attachment; filename="habits_export_YYYYMMDD_HHMMSS.csv"`

#### Export JSON
```http
GET /api/habits/export/json/
```
- **Description**: Download all habits and logs as JSON
- **Auth**: Required
- **Response**: JSON file download
- **Headers**:
  - `Content-Type: application/json`
  - `Content-Disposition: attachment; filename="habits_export_YYYYMMDD_HHMMSS.json"`
- **Response Body**:
  ```json
  {
    "user": "john_doe",
    "export_date": "2026-02-02T14:32:10.123456",
    "habits": [
      {
        "name": "Morning Meditation",
        "category": "health",
        "frequency": "daily",
        "goal_count": 1,
        "start_date": "2026-02-01",
        "streak_count": 3,
        "longest_streak": 5,
        "logs": [
          {
            "date": "2026-02-01",
            "completed": true
          }
        ]
      }
    ]
  }
  ```

#### Update Log
```http
PATCH /api/habit-logs/{id}/
```
- **Description**: Update a habit log entry
- **Auth**: Required (must own related habit)
- **Request Body**: Any subset of log fields
- **Response**: Updated log object (200)

---

## Response Formats

### Success Response (200, 201)
```json
{
  "id": 1,
  "name": "Morning Run",
  "category": "health",
  "frequency": "daily",
  "goal_count": 1,
  "is_active": true,
  "current_streak": 3,
  "longest_streak": 5,
  "completion_rate": 0.60,
  "logs": [
    {
      "id": 1,
      "date": "2026-02-01",
      "completed": true,
      "notes": "5K in 25 mins",
      "created_at": "2026-02-01T08:15:00Z"
    }
  ],
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-02-01T08:15:00Z"
}
```

### Error Response (4xx, 5xx)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

or

```json
{
  "field_name": ["Error message"]
}
```

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE (no content in response) |
| 205 | Reset Content | Successful logout |
| 400 | Bad Request | Validation error, duplicate log |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Authenticated but not allowed to access |
| 404 | Not Found | Resource doesn't exist or not owned by user |
| 500 | Server Error | Unexpected server error |

---

## Pagination

List endpoints use page-based pagination. Default page size is 20 items.

**Response Format:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/habits/?page=2",
  "previous": null,
  "results": [...]
}
```

**Query Parameters:**
- `page`: Page number (default: 1)
- To specify page size, use: `?page=1&page_size=50`

---

## Error Handling

### Common Errors

**401 Unauthorized - Missing Authentication**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**401 Unauthorized - Invalid Token**
```json
{
  "detail": "Given token not valid for any token type"
}
```

**400 Bad Request - Validation Error**
```json
{
  "name": ["This field may not be blank."],
  "start_date": ["This field is required."]
}
```

**400 Bad Request - Duplicate Log**
```json
{
  "detail": "A log for this habit already exists for this date."
}
```

**404 Not Found**
```json
{
  "detail": "Not found."
}
```

---

## Field Constraints

### Habit Fields
- **name**: Required, string, max 100 chars
- **description**: Optional, string, max 500 chars
- **category**: Required, choice (see list above)
- **frequency**: Required, choice (daily, weekly, monthly)
- **goal_count**: Optional, positive integer (default: 1)
- **start_date**: Required, date format YYYY-MM-DD
- **is_active**: Optional, boolean (default: true)

### Habit Log Fields
- **date**: Required, date format YYYY-MM-DD
- **completed**: Required, boolean
- **notes**: Optional, string, max 500 chars

---

## Examples

### Example: Complete User Flow

**1. Register**
```bash
curl -X POST http://localhost:8000/api/auth/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sarah",
    "email": "sarah@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

**2. Create Habit**
```bash
curl -X POST http://localhost:8000/api/habits/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Meditation",
    "category": "health",
    "frequency": "daily",
    "start_date": "2026-02-01"
  }'
```

**3. Log Completion**
```bash
curl -X POST http://localhost:8000/api/habits/1/log/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-01",
    "completed": true,
    "notes": "Morning session"
  }'
```

**4. Check Stats**
```bash
curl -X GET http://localhost:8000/api/habits/1/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Testing the API

### Using Swagger UI (Recommended)
1. Navigate to `http://localhost:8000/api/docs/`
2. Click "Authorize" button
3. Enter your JWT token: `Bearer <access_token>`
4. Try endpoints interactively with "Try It Out"

### Using cURL
See examples above

### Using Postman
1. Import the OpenAPI schema: `http://localhost:8000/api/schema/`
2. Add token to Authorization tab
3. Use the generated requests

### Using Python/Requests
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}

# Get all habits
response = requests.get("http://localhost:8000/api/habits/", headers=headers)
print(response.json())
```

---

## Rate Limiting

Currently no rate limiting implemented. Plan for future versions.

---

## Versioning

API Version: **1.0.0**

Future versions will use URL versioning: `/api/v2/habits/`

---

## Support

For issues or questions about the API:
- Check `/api/docs/` for interactive documentation
- Review error messages carefully
- Ensure authentication tokens are valid and not expired
- Verify request data matches schema requirements

---

**Last Updated**: February 1, 2026
**Status**: Production Ready
