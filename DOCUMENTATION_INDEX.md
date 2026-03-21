# 📚 Documentation Index

## 🚀 Getting Started

### **START_HERE.md** 
**Read this first!** Quick orientation and links to other docs.
- 2-minute quick start
- What's been built
- Troubleshooting
- Command reference

### **QUICK_START_GUIDE.md**
Fast path to running the application.
- Prerequisites installation
- Step-by-step startup
- Common commands
- Service URLs

### **COMPLETE_SETUP_GUIDE.md**
Detailed comprehensive guide.
- Full architecture explanation
- Every command explained
- Environment variables
- Production deployment
- Complete troubleshooting

---

## 🔧 Integration & Development

### **FRONTEND_INTEGRATION_COMPLETE.md**
Frontend details and API integration.
- All pages and features listed
- Component structure
- API connection details
- Technology stack
- Usage examples
- Learning resources

### **frontend/.env**
Environment variables for frontend.
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=AI Adaptive Onboarding Engine
```

### **startup.bat**
One-click Windows startup script.
- Checks prerequisites
- Starts Docker services
- Installs npm packages
- Starts frontend dev server

### **startup.ps1**
Advanced PowerShell startup script.
- Full prerequisite checking
- Service status reporting
- Log monitoring
- Multiple startup options

---

## 🛠️ Startup Scripts

### Option 1: Batch File (Easiest)
```powershell
.\startup.bat
```
Run this from the project root directory.

### Option 2: PowerShell Script
```powershell
.\startup.ps1 start
.\startup.ps1 logs
.\startup.ps1 status
.\startup.ps1 stop
```

### Option 3: Manual Steps
```powershell
# Terminal 1
docker-compose up -d

# Terminal 2
cd frontend
npm install
npm run dev
```

---

## 📁 Frontend Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.jsx          ← Authentication
│   │   ├── Register.jsx       ← User signup
│   │   ├── Dashboard.jsx      ← Main dashboard
│   │   ├── Programs.jsx       ← Program management
│   │   ├── Analytics.jsx      ← Analytics & reports
│   │   ├── Users.jsx          ← User management
│   │   └── Settings.jsx       ← Settings & config
│   │
│   ├── components/
│   │   ├── Sidebar.jsx        ← Navigation
│   │   ├── Header.jsx         ← Top bar
│   │   └── StatCard.jsx       ← Statistics card
│   │
│   ├── context/
│   │   └── AuthContext.jsx    ← Auth state management
│   │
│   ├── api/
│   │   └── client.js          ← HTTP client & endpoints
│   │
│   ├── App.jsx                ← Main app component
│   ├── index.css              ← Global styles
│   └── main.jsx               ← Entry point
│
├── public/
│   └── index.html
│
├── package.json               ← Dependencies
├── vite.config.js            ← Build config
├── tailwind.config.js        ← CSS config
├── postcss.config.js         ← PostCSS config
└── .env                       ← Environment variables
```

---

## 🖥️ Backend Structure

```
backend/
├── app/
│   ├── main.py               ← FastAPI app
│   ├── routes/               ← API endpoints
│   ├── models/               ← Database models
│   ├── schemas/              ← Data validation
│   ├── services/             ← Business logic
│   ├── core/                 ← Configuration
│   └── llm/                  ← LLM providers
│
├── tests/                    ← Test suite
├── scripts/                  ← Utility scripts
├── Dockerfile               ← Container definition
├── docker-compose.yml       ← Multi-container setup
├── requirements.txt         ← Python dependencies
└── API_DOCUMENTATION.md     ← API reference
```

---

## 📖 API Documentation

### **backend/API_DOCUMENTATION.md**
Complete API reference including:
- All endpoints
- Request/response examples
- Authentication details
- Error codes
- Rate limiting

### Quick API Reference

#### Authentication
```
POST   /api/v1/auth/register    ← Create account
POST   /api/v1/auth/login       ← Login
POST   /api/v1/auth/logout      ← Logout
POST   /api/v1/auth/refresh     ← Refresh token
GET    /api/v1/auth/me          ← Current user
```

#### Programs
```
GET    /api/v1/programs         ← List programs
POST   /api/v1/programs         ← Create program
GET    /api/v1/programs/{id}    ← Get program
PUT    /api/v1/programs/{id}    ← Update program
DELETE /api/v1/programs/{id}    ← Delete program
```

#### Users
```
GET    /api/v1/admin/users      ← List all users
GET    /api/v1/admin/users/{id} ← Get user details
PUT    /api/v1/admin/users/{id} ← Update user
DELETE /api/v1/admin/users/{id} ← Delete user
```

#### Analytics
```
GET    /api/v1/analytics/stats  ← Get statistics
GET    /api/v1/analytics/users  ← User analytics
GET    /api/v1/analytics/programs ← Program analytics
```

---

## 🔗 URLs & Ports

### Development
| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| API ReDoc | http://localhost:8000/redoc | 8000 |
| Database | localhost | 5432 |

### Docker Services
```
ai-onboarding-db   ← PostgreSQL database
ai-onboarding-app  ← FastAPI backend
```

---

## 🛠️ Common Commands

### Docker Management
```powershell
# View running containers
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs --tail=50

# Restart services
docker-compose restart
docker-compose restart app

# Stop services
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Frontend Management
```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database Access
```powershell
# Connect to database
docker exec -it ai-onboarding-db psql -U postgres -d ai_onboarding

# View tables
\dt

# View specific table
SELECT * FROM "user";

# Exit
\q
```

---

## 🔐 Environment Configuration

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=AI Adaptive Onboarding Engine
```

### Backend (docker-compose.yml)
```
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_onboarding
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Application
APP_ENV=development
DEBUG=true

# Security
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GEMINI_API_KEY=<your-key>
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────┐
│  React Frontend (Vite)                  │
│  • Dashboard                            │
│  • Programs, Analytics, Users           │
│  • Settings, Authentication             │
└──────────────┬──────────────────────────┘
               │
       Axios HTTP Client
       JWT Authentication
               │
┌──────────────▼──────────────────────────┐
│  FastAPI Backend Server                 │
│  • Authentication endpoints             │
│  • Program management                   │
│  • User management                      │
│  • Analytics & reporting                │
│  • LLM integration                      │
└──────────────┬──────────────────────────┘
               │
     SQLAlchemy ORM
     Pydantic validation
               │
┌──────────────▼──────────────────────────┐
│  PostgreSQL Database                    │
│  • Users, Programs, Analyses            │
│  • Audit logs, Session management       │
└─────────────────────────────────────────┘
```

---

## 🎯 Development Workflow

### Day 1: Setup
1. Install Docker Desktop
2. Install Node.js
3. Run `startup.bat`
4. Access http://localhost:3000

### Day 2: Explore
1. Login to dashboard
2. Create programs
3. Check analytics
4. Manage users
5. Configure settings

### Day 3+: Customize
1. Modify frontend components (auto-reload)
2. Add new pages/features
3. Update API endpoints
4. Test with real data

---

## 📚 Additional Resources

### Getting Started
- **START_HERE.md** - First read this
- **QUICK_START_GUIDE.md** - Fast path to running
- **COMPLETE_SETUP_GUIDE.md** - Detailed instructions

### Development
- **FRONTEND_INTEGRATION_COMPLETE.md** - Frontend deep dive
- **backend/API_DOCUMENTATION.md** - API reference
- **backend/ARCHITECTURE.md** - System design

### Reference
- React: https://react.dev
- FastAPI: https://fastapi.tiangolo.com
- Tailwind CSS: https://tailwindcss.com
- Vite: https://vitejs.dev

---

## 🐛 Troubleshooting Quick Links

Problem | Solution
--------|----------
`npm: command not found` | Install Node.js, restart computer
`Port already in use` | Kill process or use different port
`Docker daemon not running` | Start Docker Desktop
`Backend not responding` | Check logs: `docker-compose logs app`
`Can't connect to database` | Restart: `docker-compose restart db`

---

## ✅ Verification Steps

Confirm everything works:

1. **Docker running**
   ```powershell
   docker --version
   docker-compose ps
   ```

2. **Backend responding**
   - Visit http://localhost:8000/docs
   - Should show Swagger UI

3. **Frontend running**
   - Visit http://localhost:3000
   - Should show login page

4. **Can login**
   - Use provided credentials
   - Should see dashboard

5. **No console errors**
   - F12 → Console
   - No red error messages

---

## 🚀 Quick Start Commands

```powershell
# One-liner quick start
cd "c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main" && .\startup.bat

# Or manually
docker-compose up -d && cd frontend && npm run dev
```

---

## 📞 Support

If you get stuck:
1. Check relevant documentation above
2. View logs: `docker-compose logs -f`
3. Check browser console: F12
4. Review the COMPLETE_SETUP_GUIDE.md

---

**Last Updated:** March 2026
**Frontend Status:** ✅ Complete - 7 pages, 3 components, full API integration
**Backend Status:** ✅ Running via Docker - FastAPI + PostgreSQL
**Documentation:** ✅ Comprehensive - 4 main guides + this index
