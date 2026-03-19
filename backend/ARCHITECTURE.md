# Architecture Overview

## System Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Service                   │
│                    ────────────────────                       │
├─────────────────────────────────────────────────────────────┤
│                         API Routes                           │
│  POST /analyze  |  GET /analysis/:id  |  POST /users         │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Resume Parser    │ Skill Extractor   │ Skill Gap     │   │
│  │ Learning Path Gen │ File Handler     │ Utilities     │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer (SQLAlchemy ORM)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Database Queries & Models                  │   │
│  │        (Users, Analyses, Relationships)              │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                  PostgreSQL Database                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  users Table   │   analyses Table   │  JSON Fields   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

### 1. Core Module (`app/core/`)
- **config.py**: Application configuration management using Pydantic Settings
  - Environment variable loading
  - Lazy initialization with caching
  - Database URL construction

- **database.py**: SQLAlchemy setup and session management
  - Engine creation with connection pooling
  - Session factory for dependency injection
  - Database initialization on startup

### 2. Models Module (`app/models/`)
- **user.py**: User ORM model
  - User account information
  - Relationship to analyses
  - Cascade delete configuration

- **analysis.py**: Analysis result ORM model
  - Stores resume/JD text
  - JSON fields for complex data
  - Relationship to users
  - Timestamps for audit trail

### 3. Schemas Module (`app/schemas/`)
- **user_schema.py**: Pydantic validation schemas for users
  - Request validation (UserCreate)
  - Response models (UserResponse)
  - Database models (UserInDB)

- **analysis_schema.py**: Pydantic validation schemas for analysis
  - Complex nested models
  - Learning path structure
  - Reasoning trace format
  - Response serialization

### 4. Services Module (`app/services/`)
- **resume_parser.py**: Resume information extraction
  - Education extraction
  - Experience level detection
  - Project identification
  - Heuristic-based analysis

- **skill_extractor.py**: Skill extraction engine
  - Rule-based matching with skill database
  - LLM integration placeholder
  - Skill normalization
  - Alias resolution

- **skill_gap.py**: Skill comparison and gap analysis
  - Matched skills identification
  - Missing skills categorization
  - Priority ranking based on JD context
  - Match percentage calculation

- **learning_path.py**: Adaptive learning path generation
  - User skill level detection
  - Personalized learning steps
  - Resource recommendation
  - Reasoning explanation generation

### 5. Routes Module (`app/routes/`)
- **analysis_routes.py**: API endpoint definitions
  - User CRUD operations
  - Analysis processing workflow
  - Result retrieval endpoints
  - Health checks

### 6. Utils Module (`app/utils/`)
- **file_handler.py**: File processing utilities
  - PDF text extraction with pdfplumber
  - TXT file handling
  - File validation (type, size)
  - Error handling

- **skill_knowledge_base.py**: Skill learning database
  - 20+ technology skills
  - Multi-level learning paths
  - Resource links
  - Time estimates

## Data Flow

### Analysis Processing Workflow

```
1. File Upload
   ↓
2. Validation (file type, size)
   ↓
3. Text Extraction (PDF/TXT)
   ↓
4. Skill Extraction (Rule-based)
   ├─ Resume → Resume Skills
   └─ JD → JD Skills
   ↓
5. Skill Gap Analysis
   ├─ Find Matched Skills
   ├─ Find Missing Skills
   └─ Categorize by Priority
   ↓
6. User Level Detection
   ├─ Parse Resume
   └─ Infer Experience Level
   ↓
7. Adaptive Learning Path Generation
   ├─ Generate Learning Steps
   ├─ Fetch Resources
   └─ Calculate Time Estimates
   ↓
8. Reasoning Generation
   ├─ Explain Missing Skills
   ├─ Highlight Matched Skills
   └─ Provide Context
   ↓
9. Database Storage
   ├─ Save Analysis Record
   ├─ Store All Extracted Data
   └─ Create Relationships
   ↓
10. Response Formatting & Return
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
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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

## JSON Data Structures

### Learning Path Example
```json
[
  {
    "skill": "React",
    "current_level": "beginner",
    "target_level": "intermediate",
    "steps": [
      "Learn JSX syntax",
      "Master state and props",
      "Understand hooks"
    ],
    "resources": [
      {
        "title": "React Official Docs",
        "url": "https://react.dev",
        "type": "documentation"
      }
    ],
    "estimated_hours": 50,
    "priority": "high"
  }
]
```

### Reasoning Trace Example
```json
[
  {
    "skill": "React",
    "reason": "React is required in the job description but was not found in your resume.",
    "missing": true
  },
  {
    "skill": "JavaScript",
    "reason": "JavaScript matches between your resume and job description.",
    "missing": false
  }
]
```

## Design Patterns Used

### 1. Dependency Injection
- FastAPI `Depends()` for database sessions
- Service layer receives dependencies
- Promotes testability and loose coupling

### 2. Repository Pattern
- SQLAlchemy models as data access layer
- Separation of data access from business logic

### 3. Service Layer Pattern
- Business logic in dedicated service modules
- Routes delegate to services
- Promotes code reusability

### 4. Factory Pattern
- Settings factory with caching (`@lru_cache`)
- Database session factory

### 5. Strategy Pattern
- Multiple extraction strategies (rule-based, LLM-ready)
- Easy to switch implementations

## Extension Points

### 1. LLM Integration
```python
# In skill_extractor.py
async def extract_skills_with_llm(text, api_key):
    # Placeholder for actual LLM API calls
    # Can be swapped with OpenAI, Claude, Llama, etc.
```

### 2. Authentication
- Add AuthenticationRouter before analysis routes
- Implement JWT token validation
- Use FastAPI Security dependency

### 3. Caching
- Add Redis for skill knowledge base caching
- Cache analysis results for repeated queries
- Use FastAPI caching middleware

### 4. Notifications
- Email notifications on analysis completion
- WebSocket support for real-time updates
- Progress notifications during processing

### 5. Advanced Analytics
- User progress tracking
- Skill adoption metrics
- Learning effectiveness analysis
- Dashboard with visualizations

## Performance Considerations

1. **Database Optimization**
   - Connection pooling (pool_size=10, max_overflow=20)
   - Proper indexing on frequently queried fields
   - JSON field optimization for complex data

2. **File Processing**
   - Streaming for large PDFs
   - Async file I/O
   - Validation before processing

3. **Memory Management**
   - Lazy loading of knowledge base
   - Caching of frequently accessed data
   - Proper resource cleanup

4. **Scalability**
   - Stateless API design
   - Horizontal scaling ready
   - Database connection pooling

## Security Features

1. **Input Validation**
   - Pydantic validation for all inputs
   - File type and size validation
   - Email validation

2. **SQL Injection Prevention**
   - SQLAlchemy ORM (parameterized queries)
   - No raw SQL queries

3. **CORS & Middleware**
   - CORS middleware for frontend integration
   - Trusted host validation
   - Error handling with proper status codes

4. **Environment Protection**
   - Environment variables for secrets
   - No credentials in code
   - .env in .gitignore

## Future Enhancements

1. **Authentication & Authorization**
   - JWT token-based auth
   - Role-based access control
   - OAuth2 integration

2. **Real-time Features**
   - WebSocket support
   - Live progress updates
   - Collaborative features

3. **ML Enhancements**
   - Custom ML models for skill extraction
   - Better experience level detection
   - Recommendation engines

4. **Integration**
   - LinkedIn API integration
   - GitHub profile analysis
   - Third-party skill assessment APIs

5. **User Experience**
   - Progress tracking dashboard
   - Skill badges and certifications
   - Community features
   - Achievement systems
