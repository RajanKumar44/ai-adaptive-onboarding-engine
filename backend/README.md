# AI Adaptive Onboarding Engine - Backend

Production-ready FastAPI backend system for intelligent resume-to-job matching with personalized learning paths.

## Features

- **Resume & Job Description Analysis**: Extract skills from PDF/TXT files
- **Intelligent Skill Extraction**: Rule-based and LLM-ready skill detection
- **Skill Gap Analysis**: Identify missing skills with priority categorization
- **Adaptive Learning Paths**: Generate personalized learning roadmaps
- **Reasoning Trace**: Detailed explanations for each recommendation
- **PostgreSQL Database**: Persistent storage with SQLAlchemy ORM
- **FastAPI Framework**: Modern, fast, production-ready API
- **Modular Architecture**: Clean separation of concerns
- **LLM Integration Ready**: Placeholder for OpenAI/Claude integration

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # Main application entry point
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── database.py         # SQLAlchemy setup
│   ├── models/
│   │   ├── user.py             # User database model
│   │   └── analysis.py         # Analysis database model
│   ├── schemas/
│   │   ├── user_schema.py      # User Pydantic schemas
│   │   └── analysis_schema.py  # Analysis Pydantic schemas
│   ├── routes/
│   │   └── analysis_routes.py  # API endpoints
│   ├── services/
│   │   ├── resume_parser.py    # Resume parsing logic
│   │   ├── skill_extractor.py  # Skill extraction (rule-based + LLM ready)
│   │   ├── skill_gap.py        # Skill gap analysis logic
│   │   └── learning_path.py    # Learning path generation
│   └── utils/
│       ├── file_handler.py     # PDF/TXT file processing
│       └── skill_knowledge_base.py  # Skill learning database
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip or conda

### Setup Steps

1. **Clone Repository**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   # Edit .env file with your PostgreSQL credentials
   cp .env.example .env
   # Update POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
   ```

5. **Start PostgreSQL**
   ```bash
   # macOS with Homebrew
   brew services start postgresql
   
   # Linux
   sudo systemctl start postgresql
   
   # Windows (via pgAdmin or command line)
   ```

6. **Run Application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access API**
   - API Documentation: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc
   - API Root: http://localhost:8000/

## API Endpoints

### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe"
}
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

### Analyze Resume & Job Description
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

- user_id: 1
- resume_file: (PDF or TXT file)
- jd_file: (PDF or TXT file)
```

**Response:**
```json
{
  "analysis_id": 1,
  "user_id": 1,
  "resume_skills": ["Python", "FastAPI", "SQL"],
  "jd_skills": ["Python", "FastAPI", "SQL", "React", "Docker"],
  "matched_skills": ["Python", "FastAPI", "SQL"],
  "missing_skills": ["React", "Docker"],
  "gap_analysis": {
    "match_percentage": 60.0,
    "total_jd_skills": 5,
    "matched_count": 3,
    "missing_count": 2
  },
  "learning_path": [
    {
      "skill": "React",
      "current_level": "intermediate",
      "target_level": "advanced",
      "steps": ["Learn React hooks", "Master component lifecycle", ...],
      "resources": [...],
      "estimated_hours": 80,
      "priority": "high"
    },
    {
      "skill": "Docker",
      "current_level": "beginner",
      "target_level": "intermediate",
      "steps": [...],
      "resources": [...],
      "estimated_hours": 45,
      "priority": "high"
    }
  ],
  "reasoning": [
    {
      "skill": "React",
      "reason": "React is required in the job description but was not found in your resume.",
      "missing": true
    },
    {
      "skill": "Python",
      "reason": "Python matches between your resume and job description.",
      "missing": false
    }
  ],
  "estimated_learning_hours": 125,
  "user_experience_level": "intermediate"
}
```

### Retrieve Analysis
```http
GET /api/v1/analysis/{analysis_id}
```

**Response:** Complete analysis data

### Get User's Analyses
```http
GET /api/v1/users/{user_id}/analyses
```

**Response:**
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
    }
  ]
}
```

### Health Check
```http
GET /api/v1/health
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Analyses Table
```sql
CREATE TABLE analyses (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL FOREIGN KEY REFERENCES users(id),
  resume_text TEXT NOT NULL,
  jd_text TEXT NOT NULL,
  extracted_resume_skills JSON NOT NULL,
  extracted_jd_skills JSON NOT NULL,
  missing_skills JSON NOT NULL,
  matched_skills JSON NOT NULL,
  learning_path JSON NOT NULL,
  reasoning_trace JSON NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Skill Knowledge Base

The system includes a comprehensive skill knowledge base with learning paths for 20+ technologies:

- **Programming Languages**: Python, JavaScript, TypeScript, Java, C++
- **Frontend**: React, Vue, Angular
- **Backend**: FastAPI, Django, Spring Boot, Express
- **Databases**: SQL, MongoDB, Redis, PostgreSQL
- **DevOps**: Docker, Kubernetes, AWS, Git, CI/CD
- **And more...**

Each skill includes:
- Beginner, intermediate, and advanced learning steps
- Curated learning resources and tutorials
- Estimated learning hours for each level
- Prerequisites and skill dependencies

## LLM Integration (Ready for Production)

The system is designed for easy LLM integration. The `extract_skills_with_llm()` function in `skill_extractor.py` has placeholders for:

- **OpenAI GPT-4**: Uncomment and add API key
- **Anthropic Claude**: Easy integration available
- **Any LLM Provider**: Flexible design for custom implementations

To enable LLM-based extraction:

1. Install provider SDK:
   ```bash
   pip install openai  # or anthropic, etc.
   ```

2. Uncomment API call in `app/services/skill_extractor.py`

3. Add API key to `.env`:
   ```
   LLM_API_KEY=your-api-key
   LLM_PROVIDER=openai
   ```

4. Use in endpoint:
   ```python
   skills = await SkillExtractor.extract_skills(text, use_llm=True, api_key=api_key)
   ```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Formatting
black app/

# Linting
pylint app/

# Type checking
mypy app/
```

### Database Migrations
```bash
# Using Alembic
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

## Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong PostgreSQL password
- [ ] Configure CORS origins (not `*`)
- [ ] Configure trusted hosts
- [ ] Set up environment variables properly
- [ ] Enable HTTPS/SSL
- [ ] Configure database backups
- [ ] Set up monitoring and logging
- [ ] Add rate limiting
- [ ] Implement authentication/authorization
- [ ] Use connection pooling for database
- [ ] Deploy with Gunicorn or similar ASGI server

## Performance Optimization

- Connection pooling enabled by default
- Query optimization with proper indexing
- Async/await for I/O operations
- File streaming for large PDFs
- Caching for skill knowledge base

## Security Features

- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- CORS middleware
- Trusted host validation
- File type and size validation
- Environment variable protection

## Monitoring & Logging

- Health check endpoint
- Error exception handlers
- PostgreSQL query logging (debug mode)
- Request/response logging ready

## Support & Documentation

- Interactive API docs: `/api/v1/docs`
- ReDoc documentation: `/api/v1/redoc`
- Comprehensive code comments
- Docstrings for all functions

## Future Enhancements

- [ ] User authentication (JWT)
- [ ] Email notifications
- [ ] Progress tracking
- [ ] Skill assessment quizzes
- [ ] Advanced analytics dashboard
- [ ] Integration with learning platforms
- [ ] Real-time progress updates (WebSockets)
- [ ] Admin panel

## License

MIT License - See LICENSE file

## Contact

For questions or support, please open an issue or contact the development team.
