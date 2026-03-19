# AI Adaptive Onboarding Engine

An intelligent backend system that analyzes resumes and job descriptions to generate personalized adaptive learning roadmaps for skill development.

## 🚀 Quick Overview

This project provides a **production-ready FastAPI backend** that:
- Extracts and analyzes skills from resumes and job descriptions
- Identifies skill gaps with intelligent prioritization
- Generates personalized learning paths with estimated learning hours
- Explains recommendations with detailed reasoning traces
- Persists all analysis results in PostgreSQL

## 📁 Project Structure

```
ai-adaptive-onboarding-engine/
├── backend/                    # Main backend application (START HERE!)
│   ├── app/                    # FastAPI application code
│   │   ├── main.py            # Application entry point
│   │   ├── core/              # Configuration & database setup
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic (parsing, extraction, analysis)
│   │   └── utils/             # Utilities & knowledge bases
│   ├── requirements.txt        # Python dependencies
│   ├── .env                   # Configuration (create from .env.example)
│   ├── docker-compose.yml     # PostgreSQL setup
│   ├── Makefile               # Useful commands
│   └── README.md              # Backend documentation
├── README.md                  # This file
└── .git/                      # Version control

```

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.104.1 |
| **Language** | Python 3.9+ |
| **Database** | PostgreSQL 12+ |
| **ORM** | SQLAlchemy 2.0.23 |
| **Validation** | Pydantic 2.5.0 |
| **File Processing** | pdfplumber 0.10.3 |
| **Server** | Uvicorn 0.24.0 |
| **Containerization** | Docker & Docker Compose |

## ⚡ Getting Started

### 1. Navigate to Backend
```bash
cd backend
```

### 2. Follow Setup Instructions
See [backend/README.md](backend/README.md) for complete installation and setup guide.

### 3. Quick Commands
```bash
# Copy environment template
cp .env.example .env

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start database (Docker)
docker-compose up -d

# Run application
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/users` | Create a new user |
| `POST` | `/api/v1/analyze` | Analyze resume & job description |
| `GET` | `/api/v1/analysis/{id}` | Retrieve specific analysis |
| `GET` | `/api/v1/users/{id}/analyses` | List user's analyses |
| `GET` | `/health` | Health check |

For detailed API documentation, see [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md).

## 📖 Documentation

All documentation is located in the `backend/` folder:

| Document | Purpose |
|----------|---------|
| [backend/README.md](backend/README.md) | Backend setup & overview |
| [backend/QUICKSTART.md](backend/QUICKSTART.md) | Quick local setup guide |
| [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md) | System design & architecture |
| [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) | Cloud deployment guides |
| [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md) | Detailed API reference |

## 🏗️ Architecture Highlights

- **Modular Design**: Separated concerns (routes, services, models, schemas)
- **Service Layer**: Business logic isolated from API layer
- **Dependency Injection**: Clean, testable code structure
- **Error Handling**: Comprehensive validation and error responses
- **Async Support**: FastAPI async capabilities for high performance
- **Database Optimization**: Connection pooling and session management
- **Production Ready**: Security headers, CORS, input validation

## 🛠️ Key Features

✅ **Resume & Job Description Analysis**
  - PDF and text file extraction
  - Automatic skill detection

✅ **Intelligent Skill Extraction**
  - Rule-based pattern matching
  - LLM integration ready (OpenAI/Claude placeholder)
  - 20+ technology coverage

✅ **Skill Gap Analysis**
  - Resume vs. JD comparison
  - Missing skills identification
  - Priority categorization (critical/important/nice-to-have)

✅ **Personalized Learning Paths**
  - Multi-level learning roadmaps (beginner → advanced)
  - Estimated learning hours per skill
  - Resource recommendations with URLs

✅ **Reasoning Trace**
  - Detailed explanations for each recommendation
  - Skill prioritization justification
  - Learning path rationale

✅ **Data Persistence**
  - PostgreSQL database storage
  - SQLAlchemy ORM relationships
  - JSON field support for complex data

## 🐳 Docker Support

The project includes Docker setup for easy deployment:

```bash
# Start PostgreSQL and application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_analysis.py -v
```

## 📦 Dependencies

All dependencies are managed in `backend/requirements.txt`:
- Production dependencies: FastAPI, SQLAlchemy, Pydantic, pdfplumber, etc.
- Development dependencies: pytest, black, pylint, mypy, flake8

## 🚢 Deployment

The project supports deployment to:
- **AWS**: EC2, ECS, App Runner
- **Azure**: App Service, Container Instances
- **Google Cloud**: Cloud Run, Compute Engine
- **Docker**: Any container orchestration platform

See [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) for detailed instructions.

## 📝 License

MIT License - see LICENSE file for details

## 👥 Support

For issues, questions, or contributions:
1. Check [backend/README.md](backend/README.md) for common setup issues
2. Review [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) for deployment help
3. Check API documentation at http://localhost:8000/docs once running

---

**Ready to start?** Go to the [backend folder](backend/) and follow the setup guide!