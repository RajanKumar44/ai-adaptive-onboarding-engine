# Phase 1 Security Implementation Guide

Complete security implementation including JWT authentication, role-based access control, rate limiting, and password management.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Security Features](#security-features)
3. [Authentication Flow](#authentication-flow)
4. [User Roles](#user-roles)
5. [API Endpoints](#api-endpoints)
6. [Configuration](#configuration)
7. [Usage Examples](#usage-examples)
8. [Best Practices](#best-practices)

---

## Overview

Phase 1 implements enterprise-grade security with JWT-based authentication, role-based access control, and rate limiting to protect the application from unauthorized access and abuse.

### What's New
- ✅ User registration and login with JWT tokens
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (admin/user/guest)
- ✅ Rate limiting on endpoints
- ✅ API key authentication support
- ✅ Password strength validation
- ✅ Authorization checks for data access

---

## Security Features

### 1. JWT Authentication

**Technology**: `python-jose` for JWT handling

**Features**:
- Access tokens (30-minute expiration)
- Refresh tokens (7-day expiration)
- Token-based stateless authentication
- Bearer token format

**Example Token**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3MDExMjM0NTgsInR5cGUiOiJhY2Nlc3MifQ.signature
```

### 2. Password Hashing

**Technology**: `bcrypt` with `passlib`

**Strength Validation**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Configuration** (in `.env`):
```env
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGITS=True
PASSWORD_REQUIRE_SPECIAL=True
```

### 3. Role-Based Access Control (RBAC)

**Roles**:
- **Admin**: Full system access, user management
- **User**: Can create analyses, manage own data
- **Guest**: Read-only access (prepared for future use)

**User Model Updated**:
```python
class User(Base):
    __tablename__ = "users"
    
    id: int
    email: str (unique)
    name: str
    password_hash: str      # NEW
    role: UserRole          # NEW (admin/user/guest)
    is_active: bool         # NEW
    created_at: datetime
    updated_at: datetime    # NEW
```

### 4. Rate Limiting

**Technology**: `slowapi` (Starlette rate limiter)

**Rate Limits by Endpoint**:
```
Authentication:
  - Login: 5 requests/minute
  - Register: 3 requests/minute
  - Refresh Token: 10 requests/minute

Analysis:
  - POST /analyze: 10 requests/minute

General:
  - Default: 60 requests/minute
  - Hourly: 1000 requests/hour

Health:
  - Health Check: 60 requests/minute
```

### 5. API Key Authentication

Optional API key authentication for service-to-service communication.

**Configuration**:
```env
API_KEYS=key1,key2,key3
```

**Usage**:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/endpoint
```

### 6. CORS Protection

**Configuration** (in `.env`):
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

**Default**: Localhost ports for development

---

## Authentication Flow

### Registration Flow
```
1. POST /api/v1/auth/register
   ├─ Validate email format
   ├─ Check password strength
   ├─ Verify passwords match
   ├─ Check email uniqueness
   ├─ Hash password with bcrypt
   ├─ Create user in database
   └─ Return access & refresh tokens

2. Client stores tokens (securely)
   ├─ Access token: LocalStorage/Memory (30 min)
   └─ Refresh token: HttpOnly cookie (7 days)
```

### Login Flow
```
1. POST /api/v1/auth/login
   ├─ Find user by email
   ├─ Verify password (bcrypt comparison)
   ├─ Check user is active
   ├─ Generate access token
   └─ Return access & refresh tokens

2. Client uses tokens for API requests
```

### Token Refresh Flow
```
1. POST /api/v1/auth/refresh
   ├─ Receive refresh token
   ├─ Verify token validity
   ├─ Extract user_id from token
   ├─ Generate new access token
   └─ Return new access & refresh tokens
```

### Authenticated Request Flow
```
1. Client sends request with Authorization header
   GET /api/v1/analysis/123
   Authorization: Bearer <access_token>

2. Server verifies token
   ├─ Extract token from header
   ├─ Decode JWT signature
   ├─ Check expiration time
   ├─ Validate token type (access)
   ├─ Get user_id from token payload
   └─ Load user from database

3. Check authorization
   ├─ If admin: allow all actions
   ├─ If user: check data ownership
   └─ If guest: read-only

4. Execute endpoint logic
5. Return response
```

---

## User Roles

### Admin Role
```
Permissions:
  - Create/read/update/delete own account
  - View all users and their analyses
  - Manage user roles and deactivation
  - Access admin endpoints
  - Full API access

Endpoints:
  - All /api/v1/auth/* endpoints
  - All /api/v1/analyze endpoints
  - All /api/v1/admin/* endpoints (admin management)
```

### User Role
```
Permissions:
  - Create/read/update own account
  - Create and view own analyses
  - Cannot view other users' data
  - Cannot access admin endpoints

Endpoints:
  - POST /api/v1/auth/register
  - POST /api/v1/auth/login
  - GET /api/v1/auth/me
  - PUT /api/v1/auth/me
  - POST /api/v1/auth/change-password
  - POST /api/v1/analyze
  - GET /api/v1/analysis/{own_id}
  - GET /api/v1/users/{own_id}/analyses
```

### Guest Role
```
Permissions:
  - Read-only access (future implementation)
  - Cannot modify any data
  - Cannot create analyses

Endpoints:
  - Limited to read operations
  - No write/modify/delete permissions
```

---

## API Endpoints

### Authentication Endpoints

#### 1. Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}

Response (201):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}

Rate Limit: 3/minute
```

#### 2. Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}

Rate Limit: 5/minute
```

#### 3. Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}

Rate Limit: 10/minute
```

#### 4. Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGc...

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

#### 5. Update Profile
```http
PUT /api/v1/auth/me
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com"
}

Response (200):
{
  "id": 1,
  "email": "jane@example.com",
  "name": "Jane Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

#### 6. Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "confirm_password": "NewSecurePass456!"
}

Response (200):
{
  "message": "Password changed successfully",
  "status": "success"
}
```

#### 7. Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGc...

Response (200):
{
  "message": "Successfully logged out user user@example.com",
  "status": "success"
}

Note: Client should delete stored tokens
```

### Admin Endpoints

#### List All Users (Admin Only)
```http
GET /api/v1/admin/users?skip=0&limit=10
Authorization: Bearer eyJhbGc... (admin token)

Response (200):
{
  "users": [
    {
      "id": 1,
      "email": "user1@example.com",
      "name": "User 1",
      "role": "user",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "analyses_count": 5
    },
    ...
  ]
}
```

#### Get User Details (Admin Only)
```http
GET /api/v1/admin/users/{user_id}
Authorization: Bearer eyJhbGc... (admin token)

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "name": "User",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "analyses_count": 5
}
```

#### Update User Role (Admin Only)
```http
PUT /api/v1/admin/users/{user_id}/role
Authorization: Bearer eyJhbGc... (admin token)
Content-Type: application/json

{
  "new_role": "admin"
}

Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "name": "User",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-16T10:00:00"
}
```

---

## Configuration

### Environment Variables (`.env`)

```env
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGITS=True
PASSWORD_REQUIRE_SPECIAL=True

# API Keys
API_KEYS=key1,key2,key3
```

### Generating JWT Secret Key

```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
# Output: 4nC9pK2xL7mQ3wR8vB5tG1yH9dF6jU0s
```

---

## Usage Examples

### 1. Complete Authentication Flow

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# Step 1: Register
register_data = {
    "email": "john@example.com",
    "name": "John Doe",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
}

response = requests.post(
    f"{BASE_URL}/auth/register",
    json=register_data,
    headers=HEADERS
)
tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

print("✓ Registration successful")
print(f"Access Token: {access_token[:50]}...")

# Step 2: Use access token for authenticated requests
auth_headers = {
    **HEADERS,
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(
    f"{BASE_URL}/auth/me",
    headers=auth_headers
)
user = response.json()
print(f"✓ Retrieved user profile: {user['email']}")

# Step 3: Analyze resume (protected endpoint)
with open("resume.pdf", "rb") as f_resume, \
     open("job_description.txt", "rb") as f_jd:
    
    files = {
        "resume_file": f_resume,
        "jd_file": f_jd
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        files=files,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    analysis = response.json()
    print(f"✓ Analysis created: {analysis['analysis_id']}")
    print(f"  Match percentage: {analysis['gap_analysis']['match_percentage']}%")

# Step 4: Refresh token when expired
refresh_data = {"refresh_token": refresh_token}
response = requests.post(
    f"{BASE_URL}/auth/refresh",
    json=refresh_data,
    headers=HEADERS
)
new_tokens = response.json()
access_token = new_tokens["access_token"]
print(f"✓ Token refreshed")

# Step 5: Logout
response = requests.post(
    f"{BASE_URL}/auth/logout",
    headers={"Authorization": f"Bearer {access_token}"}
)
print("✓ Logged out")
```

### 2. Using cURL Commands

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Get current user (replace with actual token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Analyze resume (requires both files)
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "resume_file=@resume.pdf" \
  -F "jd_file=@job_description.txt"
```

---

## Best Practices

### 1. Token Storage

**Secure Storage**:
```javascript
// ✓ GOOD: Store in memory for SPA
const tokens = {
  accessToken: response.data.access_token,
  refreshToken: response.data.refresh_token
};

// ✓ GOOD: Store refresh token in HttpOnly cookie
document.cookie = "refresh_token=VALUE; HttpOnly; Secure; SameSite=Strict";

// ❌ AVOID: Don't store in localStorage
localStorage.setItem("access_token", response.data.access_token);
```

### 2. Handling Token Expiration

```javascript
// Automatically refresh token before expiration
const accessTokenTimeout = setTimeout(() => {
  refreshToken();
}, (30 * 60 - 60) * 1000); // Refresh 1 minute before expiry
```

### 3. Password Security

**Strong Passwords**:
- Minimum 8 characters
- Mix of uppercase and lowercase
- Numbers and special characters
- Don't reuse old passwords
- Change password regularly

**Never**:
- Store passwords in plain text
- Log passwords
- Send passwords in URLs
- Share passwords via email

### 4. JWT Best Practices

**Endpoint Security**:
```python
# Verify token in every protected endpoint
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    # Token is verified by dependency
    return current_user
```

**Short Expiration**:
- Access token: 15-30 minutes
- Refresh token: 7 days to months

**Token Signature**:
- Always verify signature
- Use secure secret key (32+ characters)
- Rotate keys periodically

### 5. Rate Limiting

**Monitor Rate Limits**:
```bash
# Check X-RateLimit headers in response
curl -i http://localhost:8000/api/v1/health

# Response includes:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 59
# X-RateLimit-Reset: 1700000000
```

### 6. CORS Configuration

**Production**:
```env
# Specific Origins Only
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Not *wildcard
```

### 7. Admin Account Management

**First Admin Setup**:
1. Register account (becomes regular user)
2. Use database admin tool to set role to "admin"
3. Or implement initial admin endpoint with secret key

```sql
UPDATE users SET role = 'admin' WHERE id = 1;
```

---

## Security Checklist

- [ ] JWT_SECRET_KEY changed in production
- [ ] CORS_ORIGINS restricted to specific domains
- [ ] Rate limiting enabled
- [ ] HTTPS enabled in production
- [ ] Password policy enforced
- [ ] Admin account properly secured
- [ ] Database backups enabled
- [ ] Logging configured
- [ ] API keys rotated regularly
- [ ] Tokens not logged or exposed
- [ ] HTTPS redirects configured
- [ ] Security headers added (future phase)

---

## Troubleshooting

### Common Issues

**Invalid Token Error**
```
Error: Invalid or expired token

Solution:
1. Check token hasn't expired (30 minutes)
2. Use refresh endpoint to get new token
3. Verify Authorization header format: "Bearer <token>"
```

**User Not Found**
```
Error: User not found

Solution:
1. Verify user exists in database
2. Check email spelling
3. Re-register if account deleted
```

**Password Doesn't Meet Requirements**
```
Error: Password must contain at least one special character

Solution:
Add special character: !@#$%^&*()
Example: SecurePass123!
```

**Rate Limited**
```
Error: rate limit exceeded

Solution:
1. Wait before making more requests
2. Check rate limit configuration
3. Space out login attempts (5 per minute)
```

---

## Next Steps

### Phase 2 (Database & Persistence)
- [ ] Implement token blacklist for logout
- [ ] Add email verification
- [ ] Implement password reset flow
- [ ] Add audit logging

### Phase 3 (Logging & Monitoring)
- [ ] Structured logging
- [ ] Request/response logging
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring

### Phase 4 (OAuth & SSO)
- [ ] Google OAuth2
- [ ] GitHub OAuth2
- [ ] Microsoft Entra ID
- [ ] LDAP integration

---

## References

- [JWT.io](https://jwt.io) - JWT specification
- [bcrypt](https://github.com/pyca/bcrypt) - Password hashing
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) - FastAPI security docs
- [OWASP Authentication](https://owasp.org/www-community/authentication) - OWASP best practices

