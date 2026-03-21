# 🚀 Complete Setup Guide - AI Adaptive Onboarding Engine

## Prerequisites
- **Docker Desktop** or Docker Engine installed
- **Node.js 18+** and npm installed
- **Git** installed
- Ports available: 3000 (frontend), 5432 (database), 8000 (backend)

## 📋 Step-by-Step Setup

### Step 1: Verify Prerequisites

```powershell
# Check Docker
docker --version
# Expected: Docker version 20.10+

# Check Docker Compose
docker-compose --version
# Expected: Docker Compose version 1.29+

# Check Node.js
node --version
# Expected: v18.0.0 or higher

# Check npm
npm --version
# Expected: npm 8.0.0 or higher
```

### Step 2: Start Backend Services

The backend uses Docker Compose to manage PostgreSQL database and FastAPI application.

```powershell
# Navigate to project root
cd "c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main"

# Stop any running containers
docker-compose down

# Start all services (database + backend API)
docker-compose up -d

# Wait 15-20 seconds for services to initialize...
```

**Verify Backend is Running:**
```powershell
# Check container status
docker-compose ps

# You should see:
# NAME                   STATUS              PORTS
# ai-onboarding-db      Up (healthy)        0.0.0.0:5432->5432/tcp
# ai-onboarding-app     Up                   0.0.0.0:8000->8000/tcp
```

**Check Backend Logs:**
```powershell
# View live logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db
```

**Access Backend Endpoints:**
- API Docs (Swagger UI): http://localhost:8000/docs
- API ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Step 3: Install Frontend Dependencies

```powershell
# Navigate to frontend directory
cd "c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main\frontend"

# Install npm packages (one-time only)
npm install

# Expected time: 2-5 minutes depending on internet speed
```

### Step 4: Start Frontend Development Server

```powershell
# From the frontend directory
npm run dev

# Expected output:
# VITE v4.4.0  ready in XXX ms
# ➜  Local:   http://localhost:3000/
# ➜  press h to show help
```

### Step 5: Access the Application

Open your browser to:

```
http://localhost:3000
```

**Default Login Credentials:**
- Email: `admin@example.com`
- Password: `password123` (or as configured in backend)

---

## 🔄 Architecture

```
┌─────────────────────────────────────────┐
│   React Frontend (Vite)                │
│   Running on: http://localhost:3000     │
│   - Dashboard                           │
│   - Programs Management                │
│   - Analytics                          │
│   - User Management                    │
│   - Settings                           │
└──────────────┬──────────────────────────┘
               │
       Axios API Client
    (Proxied to /api/*)
               │
┌──────────────▼──────────────────────────┐
│   FastAPI Backend Server                │
│   Running on: http://localhost:8000     │
│   - Authentication endpoints            │
│   - Analysis API                        │
│   - User management                     │
│   - Admin operations                    │
└──────────────┬──────────────────────────┘
               │
     SQLAlchemy ORM
               │
┌──────────────▼──────────────────────────┐
│   PostgreSQL Database                   │
│   Running on: localhost:5432            │
│   Database: ai_onboarding              │
└─────────────────────────────────────────┘
```

---

## 🛠️ Common Tasks

### View Backend Logs
```powershell
# All docker logs
docker-compose logs -f

# Just the app
docker-compose logs -f app

# Just the database
docker-compose logs -f db

# Last 50 lines
docker-compose logs --tail=50 app
```

### Stop All Services
```powershell
# Stop without removing containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

### Restart Services
```powershell
# Restart all services
docker-compose restart

# Restart just the app
docker-compose restart app

# Restart just the database
docker-compose restart db
```

### Clean Rebuild
```powershell
# Complete clean rebuild
docker-compose down -v
docker system prune -af
docker-compose build --no-cache
docker-compose up -d
```

### Database Management
```powershell
# Connect to database directly
docker exec -it ai-onboarding-db psql -U postgres -d ai_onboarding

# View database tables
\dt

# View users
SELECT * FROM "user";

# Exit psql
\q
```

---

## 📱 Frontend Features Included

✅ **Authentication Pages**
- Login page with error handling
- Registration page with password strength indicator
- Protected routes with authentication guards

✅ **Dashboard**
- User statistics cards with trend indicators
- Activity charts (line, bar, pie)
- Recent activities feed
- Quick action buttons

✅ **Programs Management**
- Create and manage onboarding programs
- Search and filter programs
- Program metrics and analytics
- Status tracking (active, draft, archived)

✅ **Analytics**
- Comprehensive data visualization
- Weekly engagement metrics
- Program performance comparison
- User progress tracking
- Top performers leaderboard

✅ **User Management**
- User table with search and filtering
- Role-based access (admin, manager, user)
- Completion rate tracking
- User actions (view, edit, delete)

✅ **Settings**
- Account settings (profile, name, email, phone)
- Organization configuration
- Notification preferences
- Security settings (2FA, session timeout)

---

## 🔌 API Configuration

The frontend connects to the backend via:

**File:** `frontend\src\api\client.js`

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1'

// All API calls are automatically authenticated with JWT token
// Token is injected in Authorization header: Bearer <token>
```

**API Endpoints Available:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/login` | POST | User login |
| `/auth/register` | POST | User registration |
| `/auth/refresh` | POST | Refresh JWT token |
| `/auth/logout` | POST | User logout |
| `/auth/me` | GET | Get current user profile |
| `/analyze` | POST | Submit analysis request |
| `/analysis/{id}` | GET | Get analysis results |
| `/admin/users` | GET | List all users |
| `/admin/users/{id}` | GET/PUT/DELETE | User management |

---

## ⚙️ Environment Variables

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=AI Adaptive Onboarding Engine
```

### Backend (docker-compose.yml)
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_onboarding
POSTGRES_HOST=db
POSTGRES_PORT=5432

APP_ENV=development
DEBUG=true

JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

LLM_PROVIDER=openai
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GEMINI_API_KEY=<your-key>
```

---

## 🐛 Troubleshooting

### "Port 3000 already in use"
```powershell
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3001
```

### "Backend not responding"
```powershell
# Check if containers are running
docker-compose ps

# View backend logs
docker-compose logs app

# Restart the service
docker-compose restart app
```

### "npm: The term 'npm' is not recognized"
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation
- Verify: `npm --version`

### "Docker daemon is not running"
- Start Docker Desktop
- On Windows, ensure WSL 2 is enabled
- Wait 30 seconds for Docker to fully start

### Database connection errors
```powershell
# Check database is healthy
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

---

## 📊 Monitoring

### Check Application Health
```powershell
# View all service logs
docker-compose logs

# Monitor resource usage
docker stats ai-onboarding-app ai-onboarding-db

# View specific error logs
docker-compose logs app | findstr ERROR
```

### Development Mode
- Hot Module Reloading (HMR) enabled
- Frontend auto-reloads on code changes
- Backend auto-reloads on code changes (via volume mount)

---

## 🚀 Production Deployment

For production deployment, refer to `DEPLOYMENT.md` in the backend directory.

Key production changes:
- Disable DEBUG mode
- Set strong JWT_SECRET_KEY
- Use environment-specific database
- Enable HTTPS/SSL
- Configure CORS properly
- Set up monitoring and logging

---

## 📚 Additional Resources

- **Backend API Docs:** [API_DOCUMENTATION.md](./backend/API_DOCUMENTATION.md)
- **Architecture Details:** [ARCHITECTURE.md](./backend/ARCHITECTURE.md)
- **Deployment Guide:** [DEPLOYMENT.md](./backend/DEPLOYMENT.md)
- **Database Setup:** [PHASE_2_DATABASE.md](./PHASE_2_DATABASE.md)

---

## ✅ Quick Checklist

Before considering setup complete:

- [ ] Docker services running (`docker-compose ps` shows all healthy)
- [ ] Backend responding at `http://localhost:8000/docs`
- [ ] Frontend dependencies installed (`npm install` completed)
- [ ] Frontend running on `http://localhost:3000`
- [ ] Can login with default credentials
- [ ] Can navigate to all pages (Dashboard, Programs, Analytics, Users, Settings)
- [ ] No console errors in browser DevTools

---

**You're all set! 🎉 Start developing!**
