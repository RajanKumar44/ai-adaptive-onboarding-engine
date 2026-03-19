# QUICKSTART GUIDE

## 30-Second Setup

### 1. Using Docker (Recommended)
```bash
cd backend

# Start PostgreSQL
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload
```

### 2. Manual PostgreSQL Setup
```bash
# macOS
brew install postgresql
brew services start postgresql

# Linux
sudo apt-get install postgresql
sudo systemctl start postgresql

# Windows
# Download from postgresql.org and install
```

### 3. Install & Run
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Testing the API

### 1. Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "John Doe"}'
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-03-20T10:30:00"
}
```

### 2. Use Postman/Swagger UI
- Go to: http://localhost:8000/api/v1/docs
- Interactive API testing
- Auto-generated API documentation

### 3. Test File Analysis
Use the Swagger UI form to upload files:
1. Navigate to POST `/api/v1/analyze`
2. Enter `user_id`: 1
3. Upload resume file (PDF or TXT)
4. Upload job description file (PDF or TXT)
5. Click "Execute"

## File Format Examples

### Resume (resume.txt)
```
John Doe
Senior Software Engineer

SKILLS
- Python: 7 years
- FastAPI: 3 years
- SQL: 7 years
- Docker: 2 years
- Git: 7 years

EXPERIENCE
Senior Backend Developer at Tech Corp (2021-Present)
- Led development of microservices architecture using FastAPI
- Managed PostgreSQL databases
- Implemented CI/CD pipelines

Backend Developer at StartupXYZ (2019-2021)
- Developed REST APIs using Python and Django
- Database design and optimization

EDUCATION
BS Computer Science - State University
```

### Job Description (jd.txt)
```
Senior Software Engineer - Backend

ABOUT THE ROLE
We are looking for an experienced backend engineer.

REQUIRED SKILLS
- Python (minimum 5 years)
- FastAPI or similar framework
- SQL and PostgreSQL
- Docker and Kubernetes
- AWS services
- Git and CI/CD
- React (nice to have)

ABOUT YOU
- Strong problem-solving skills
- Experience with microservices
- Good communication skills

RESPONSIBILITIES
- Design and implement backend systems
- Optimize database performance
- Mentor junior engineers
- Code reviews
```

## Expected Response

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
    "git",
    "react"
  ],
  "matched_skills": [
    "python",
    "fastapi",
    "sql",
    "docker",
    "git"
  ],
  "missing_skills": [
    "kubernetes",
    "aws",
    "react"
  ],
  "gap_analysis": {
    "match_percentage": 55.56,
    "total_jd_skills": 9,
    "matched_count": 5,
    "missing_count": 4
  },
  "learning_path": [
    {
      "skill": "kubernetes",
      "current_level": "beginner",
      "target_level": "intermediate",
      "steps": [
        "Kubernetes basics and concepts",
        "Pods, services, and deployments",
        "Configure YAML manifests",
        "Helm charts and templating"
      ],
      "resources": [
        {
          "title": "Kubernetes Official Documentation",
          "url": "https://kubernetes.io/docs",
          "type": "documentation"
        }
      ],
      "estimated_hours": 50,
      "priority": "high"
    },
    {
      "skill": "aws",
      "current_level": "beginner",
      "target_level": "intermediate",
      "estimated_hours": 80,
      "priority": "high"
    },
    {
      "skill": "react",
      "current_level": "beginner",
      "target_level": "intermediate",
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
      "skill": "python",
      "reason": "python matches between your resume and job description.",
      "missing": false
    }
  ],
  "estimated_learning_hours": 210,
  "user_experience_level": "advanced"
}
```

## Key Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/users` | Create new user |
| POST | `/api/v1/analyze` | Upload and analyze resume + JD |
| GET | `/api/v1/analysis/{id}` | Get specific analysis |
| GET | `/api/v1/users/{user_id}/analyses` | List user's analyses |
| GET | `/api/v1/health` | Health check |

## Database Tables

Created automatically on startup:
- `users` - Store user accounts
- `analyses` - Store analysis results

Check database with:
```bash
# macOS/Linux
psql -U postgres -d ai_onboarding

# View users
SELECT * FROM users;

# View analyses
SELECT * FROM analyses;
```

## Troubleshooting

### Port 5432 Already in Use
```bash
# Find process using port 5432
lsof -i :5432

# Kill process
kill -9 <PID>
```

### PostgreSQL Connection Error
```bash
# Check PostgreSQL status
psql -U postgres -c "SELECT 1;"

# Restart service
brew services restart postgresql  # macOS
sudo systemctl restart postgresql # Linux
```

### Module Import Error
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Not Found
```bash
# Create database
createdb -U postgres ai_onboarding

# Or via psql
psql -U postgres
CREATE DATABASE ai_onboarding;
```

## Next Steps

1. ✅ Backend API running
2. → Build Frontend (React/Vue/Angular)
3. → Add Authentication (JWT)
4. → Deploy to Cloud (AWS/Azure/GCP)
5. → Setup CI/CD Pipeline
6. → Add ML Model for better skill extraction

## Support

Documentation: http://localhost:8000/api/v1/docs
ReDoc: http://localhost:8000/api/v1/redoc
