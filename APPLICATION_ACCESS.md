# AI Adaptive Onboarding Engine - Application Access Guide

## ✅ Application Status

The application is now running! All services have been containerized and are accessible via the following endpoints:

### Frontend
- **URL**: http://localhost:3000
- **Status**: React application running via Node.js in Docker
- **Port**: 3000

### Backend API
- **URL**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Port**: 8000

### Database
- **Type**: PostgreSQL 15
- **Host**: localhost
- **Port**: 5432
- **Database**: ai_onboarding
- **Default User**: postgres
- **Default Password**: password
- **Admin Tool (Optional)**: http://localhost:8080 (run with: docker-compose --profile dev up -d)

## 🚀 Running the Application

### Option 1: Using Docker Compose (Recommended)
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (ai-onboarding-db)
- FastAPI backend (ai-onboarding-app)
- React frontend (ai-onboarding-frontend)

### Option 2: Using Windows Batch Script
```bash
startup.bat
```

### Option 3: Using PowerShell Script
```powershell
.\startup.ps1
```

## 📋 Checking Service Status

### View All Running Containers
```bash
docker-compose ps
```

### View Logs
```bash
# Frontend logs
docker-compose logs frontend -f

# Backend logs
docker-compose logs app -f

# Database logs
docker-compose logs db -f

# All logs
docker-compose logs -f
```

### Check Individual Container Status
```bash
docker inspect ai-onboarding-frontend
docker inspect ai-onboarding-app
docker inspect ai-onboarding-db
```

## 🛑 Stopping the Application

```bash
docker-compose down
```

This will stop and remove containers (data persists in volumes).

To remove everything including data:
```bash
docker-compose down -v
```

## 🔧 Troubleshooting

### Frontend Not Loading
1. Check logs: `docker-compose logs frontend`
2. Verify frontend container is running: `docker ps | findstr frontend`
3. Restart frontend: `docker-compose up -d frontend`

### Backend Issues
1. Check API is responding: Access http://localhost:8000/docs
2. View backend logs: `docker-compose logs app`
3. Verify database connection: Check app logs for "Database initialized successfully"

### Database Issues
1. Check database logs: `docker-compose logs db`
2. Verify database is healthy: `docker-compose ps` should show db as "Up (healthy)"
3. Connect directly: `docker-compose exec db psql -U postgres -d ai_onboarding`

## 🔐 Default Credentials

### Database (PostgreSQL)
- **Username**: postgres
- **Password**: password
- **Database**: ai_onboarding

### Application Features
The web application includes:
- **Authentication**: Email/password login and registration
- **Dashboard**: Overview with statistics and charts
- **Programs**: Program management and tracking
- **Analytics**: Comprehensive analytics and reporting
- **Users**: User management and administration
- **Settings**: Account and organization settings

## 📦 Technology Stack

### Frontend
- React 18.2.0
- Vite 4.4.0
- Tailwind CSS 3.3.0
- Recharts 2.7.2 (charts)
- Axios 1.4.0 (HTTP client)
- React Router 6.14.0
- Zustand 4.3.9 (state management)

### Backend
- FastAPI (Python)
- PostgreSQL 15
- SQLAlchemy ORM
- Pydantic
- JWT Authentication
- Uvicorn ASGI Server

### Infrastructure
- Docker
- Docker Compose
- Multi-container orchestration

## 🔄 Architecture

```
┌─────────────────────────────────────────────────┐
│         React Frontend (Port 3000)              │
│  ├─ Login & Registration Pages                 │
│  ├─ Dashboard with Analytics                   │
│  ├─ Program Management                         │
│  ├─ User Administration                        │
│  └─ Settings                                   │
└────────────────┬────────────────────────────────┘
                 │ HTTP/JSON (Axios)
                 ▼
┌─────────────────────────────────────────────────┐
│       FastAPI Backend (Port 8000)               │
│  ├─ Authentication & JWT                        │
│  ├─ User Management API                         │
│  ├─ Program Management API                      │
│  ├─ Analytics API                               │
│  ├─ Data Validation (Pydantic)                  │
│  └─ Async Request Handling                      │
└────────────────┬────────────────────────────────┘
                 │ SQL (SQLAlchemy)
                 ▼
┌─────────────────────────────────────────────────┐
│     PostgreSQL Database (Port 5432)             │
│  ├─ Users Table                                 │
│  ├─ Programs Table                              │
│  ├─ Analytics Data                              │
│  └─ Audit Logs                                  │
└─────────────────────────────────────────────────┘
```

## 📝 Next Steps

1. **Access the Frontend**: Open http://localhost:3000 in your browser
2. **Create an Account**: Use the registration page to create a new user
3. **Log In**: Use your credentials to access the dashboard
4. **Explore Features**: Navigate through Dashboard, Programs, Analytics, Users, and Settings
5. **Check API Documentation**: Visit http://localhost:8000/docs for API details

## ⚙️ Environment Configuration

The application uses `.env` files for configuration:

- **Backend**: `backend/.env`
- **Frontend**: `frontend/.env`
- **Database**: Configured in `docker-compose.yml`

Default values are set in each `.env` file. Modify them as needed for your setup.

## 🐛 Debug Mode

To enable debug logging:
```bash
# In backend/.env
DEBUG=true
LOG_LEVEL=DEBUG
```

To view database initialization:
```bash
docker-compose logs db --tail=50
```

## 📞 Support

For detailed API documentation, visit: http://localhost:8000/docs
For database administration (if enabled), visit: http://localhost:8080

---

**Application Setup Date**: March 21, 2026
**Docker Compose Version**: 3.8
**Status**: ✅ Ready to Use
