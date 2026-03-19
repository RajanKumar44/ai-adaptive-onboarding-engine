# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently not implemented (will be added with JWT in future versions)

## Content-Type
All requests and responses use `application/json` except file uploads which use `multipart/form-data`

---

## Endpoints

### 1. Health Check
Check if the API is running and healthy.

**HTTP Method:** `GET`
**Endpoint:** `/health`

**Request:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "AI Adaptive Onboarding Engine API",
  "version": "1.0.0"
}
```

---

### 2. Create User
Create a new user account for analysis tracking.

**HTTP Method:** `POST`
**Endpoint:** `/users`
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Required Fields:**
- `email` (string, valid email): User's email address
- `name` (string, optional): User's full name

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-03-20T10:30:00"
}
```

**Error Responses:**
- `400 Bad Request` - Email already registered
- `422 Unprocessable Entity` - Invalid email format

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe"
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/users',
    json={
        'email': 'user@example.com',
        'name': 'John Doe'
    }
)
user = response.json()
print(user['id'])  # Use this user_id for analysis
```

---

### 3. Analyze Resume & Job Description
Upload resume and job description files for skill analysis and learning path generation.

**HTTP Method:** `POST`
**Endpoint:** `/analyze`
**Content-Type:** `multipart/form-data`

**Request Parameters:**
- `user_id` (integer, required): ID of the user (from POST /users)
- `resume_file` (file, required): Resume file (PDF or TXT, max 10MB)
- `jd_file` (file, required): Job description file (PDF or TXT, max 10MB)

**Response (200 OK):**
```json
{
  "analysis_id": 1,
  "user_id": 1,
  "resume_skills": [
    "python",
    "fastapi",
    "sql",
    "docker",
    "git"
  ],
  "jd_skills": [
    "python",
    "fastapi",
    "sql",
    "postgresql",
    "docker",
    "kubernetes",
    "aws",
    "react"
  ],
  "matched_skills": [
    "python",
    "fastapi",
    "sql",
    "docker"
  ],
  "missing_skills": [
    "postgresql",
    "kubernetes",
    "aws",
    "react"
  ],
  "gap_analysis": {
    "match_percentage": 50.0,
    "total_jd_skills": 8,
    "matched_count": 4,
    "missing_count": 4
  },
  "learning_path": [
    {
      "skill": "kubernetes",
      "current_level": "beginner",
      "target_level": "intermediate",
      "steps": [
        "Learn Kubernetes basics and concepts",
        "Understand pods, services, and deployments",
        "Configure YAML manifests",
        "Helm charts and templating"
      ],
      "resources": [
        {
          "title": "Kubernetes Official Documentation",
          "url": "https://kubernetes.io/docs",
          "type": "documentation"
        },
        {
          "title": "Kubernetes Learning Lab",
          "url": "https://kubernetes.io",
          "type": "interactive"
        }
      ],
      "estimated_hours": 50,
      "difficulty": "intermediate",
      "prerequisites": [],
      "priority": "high"
    },
    {
      "skill": "aws",
      "current_level": "beginner",
      "target_level": "intermediate",
      "steps": [
        "AWS basics and core services",
        "EC2 instances and management",
        "S3 storage and bucket operations",
        "IAM roles and permissions"
      ],
      "resources": [...],
      "estimated_hours": 80,
      "difficulty": "intermediate",
      "prerequisites": [],
      "priority": "high"
    },
    {
      "skill": "react",
      "current_level": "beginner",
      "target_level": "intermediate",
      "steps": [...],
      "estimated_hours": 80,
      "priority": "medium"
    }
  ],
  "reasoning": [
    {
      "skill": "kubernetes",
      "reason": "kubernetes is required in the job description but was not found in your resume.",
      "missing": true
    },
    {
      "skill": "aws",
      "reason": "aws is required in the job description but was not found in your resume.",
      "missing": true
    },
    {
      "skill": "python",
      "reason": "python matches between your resume and job description.",
      "missing": false
    }
  ],
  "estimated_learning_hours": 210,
  "user_experience_level": "intermediate"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid file format, empty files, or text extraction failed
- `404 Not Found` - User not found
- `413 Payload Too Large` - File exceeds 10MB limit

**cURL Example (with file upload):**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "user_id=1" \
  -F "resume_file=@path/to/resume.pdf" \
  -F "jd_file=@path/to/job_description.txt"
```

**Python Example:**
```python
import requests

with open('resume.pdf', 'rb') as resume, \
     open('job_description.txt', 'rb') as jd:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze',
        data={'user_id': 1},
        files={
            'resume_file': resume,
            'jd_file': jd
        }
    )

analysis = response.json()
print(f"Matched skills: {analysis['matched_skills']}")
print(f"Missing skills: {analysis['missing_skills']}")
print(f"Learning hours: {analysis['estimated_learning_hours']}")
```

---

### 4. Get Analysis
Retrieve a previously performed analysis.

**HTTP Method:** `GET`
**Endpoint:** `/analysis/{analysis_id}`

**Path Parameters:**
- `analysis_id` (integer, required): ID of the analysis to retrieve

**Response (200 OK):**
```json
{
  "analysis_id": 1,
  "user_id": 1,
  "resume_skills": [...],
  "jd_skills": [...],
  "matched_skills": [...],
  "missing_skills": [...],
  "learning_path": [...],
  "reasoning": [...],
  "created_at": "2024-03-20T10:30:00"
}
```

**Error Responses:**
- `404 Not Found` - Analysis not found

**cURL Example:**
```bash
curl http://localhost:8000/api/v1/analysis/1
```

**Python Example:**
```python
import requests

response = requests.get('http://localhost:8000/api/v1/analysis/1')
analysis = response.json()
print(analysis['learning_path'])
```

---

### 5. Get User's Analyses
Retrieve all analyses performed by a user.

**HTTP Method:** `GET`
**Endpoint:** `/users/{user_id}/analyses`

**Path Parameters:**
- `user_id` (integer, required): ID of the user

**Response (200 OK):**
```json
{
  "user_id": 1,
  "analyses_count": 3,
  "analyses": [
    {
      "analysis_id": 1,
      "created_at": "2024-03-20T10:30:00",
      "match_percentage": 60.0,
      "missing_skills_count": 2
    },
    {
      "analysis_id": 2,
      "created_at": "2024-03-19T15:45:00",
      "match_percentage": 55.0,
      "missing_skills_count": 3
    }
  ]
}
```

**Error Responses:**
- `404 Not Found` - User not found

**cURL Example:**
```bash
curl http://localhost:8000/api/v1/users/1/analyses
```

**Python Example:**
```python
import requests

response = requests.get('http://localhost:8000/api/v1/users/1/analyses')
data = response.json()
print(f"Total analyses: {data['analyses_count']}")
for analysis in data['analyses']:
    print(f"Analysis {analysis['analysis_id']}: {analysis['match_percentage']}% match")
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Request completed |
| 201 | Created - Resource successfully created |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource not found |
| 413 | Payload Too Large - File exceeds max size |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

---

## Data Types & Formats

### Skill Object
```json
{
  "skill": "string",          // Skill name
  "current_level": "string",  // beginner, intermediate, advanced
  "target_level": "string",   // beginner, intermediate, advanced
  "steps": ["string"],        // Learning steps
  "resources": [              // Learning resources
    {
      "title": "string",
      "url": "string",
      "type": "string"        // documentation, course, tutorial, book, practice
    }
  ],
  "estimated_hours": "integer",
  "priority": "string"        // high, medium, low
}
```

### Reasoning Object
```json
{
  "skill": "string",
  "reason": "string",
  "missing": "boolean"
}
```

### Gap Analysis Object
```json
{
  "match_percentage": "number",
  "total_jd_skills": "integer",
  "matched_count": "integer",
  "missing_count": "integer"
}
```

---

## Rate Limiting
Currently not implemented but recommended to add in production:
- 100 requests per minute per user
- 1000 requests per hour per user

---

## Pagination
Not required for current implementation. Add to future versions for history listing:
```
GET /api/v1/users/{user_id}/analyses?page=1&limit=10
```

---

## WebSocket Support
Currently not implemented. Future enhancement for real-time analysis progress:
```
WS /ws/analysis/{analysis_id}
```

---

## Interactive API Documentation
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc

---

## Example Workflow

```
1. Create User
   POST /users
   → Returns user_id

2. Prepare Files
   - resume.pdf or resume.txt
   - job_description.pdf or job_description.txt

3. Analyze
   POST /analyze with user_id + files
   → Returns complete analysis with learning path

4. Retrieve Analysis
   GET /analysis/{analysis_id}
   → Get stored analysis details

5. List User History
   GET /users/{user_id}/analyses
   → See all user's analyses
```

---

## Support & Troubleshooting

### 404 Not Found
- Check that user_id exists
- Verify analysis_id is correct
- Ensure endpoint spelling is correct

### 400 Bad Request
- Verify file format (PDF or TXT)
- Check file size is under 10MB
- Ensure file is not empty
- Verify multipart form data format

### 422 Unprocessable Entity
- Email must be valid format
- Check email is not already registered
- Verify required fields are provided

### 500 Internal Server Error
- Check database connection
- Review server logs
- Restart the server
- Check Docker containers are running

---

## API Endpoints Summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Health check |
| POST | /users | Create user |
| POST | /analyze | Analyze resume + JD |
| GET | /analysis/{id} | Get analysis |
| GET | /users/{id}/analyses | List user's analyses |

---

## Future Enhancements

- [ ] JWT Authentication
- [ ] Rate limiting
- [ ] Pagination
- [ ] WebSocket for real-time updates
- [ ] Advanced filtering
- [ ] Export to PDF
- [ ] Email notifications
- [ ] Social sharing
- [ ] Mobile app API
