# 🎯 START HERE - AI Adaptive Onboarding Engine

## ⚡ Quick Start (2 Minutes)

### Prerequisites
- Windows 10/11 with Administrator access
- Docker Desktop installed: https://www.docker.com/products/docker-desktop
- Node.js LTS installed: https://nodejs.org/
- ⚠️ **After installing Node.js or Docker, RESTART your computer**

### Run This Now
```powershell
cd "c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main"
.\startup.bat
```

Done! App will open at: **http://localhost:3000**

---

## 📚 Documentation

Pick one based on your needs:

### 🚀 I want to start RIGHT NOW
→ Read: **QUICK_START_GUIDE.md**
- Fastest path to running the app
- Common issues and fixes

### 📖 I want detailed setup instructions
→ Read: **COMPLETE_SETUP_GUIDE.md**
- Step-by-step instructions
- All commands explained
- Architecture diagrams
- Production deployment

### 🔌 I want to understand the integration
→ Read: **FRONTEND_INTEGRATION_COMPLETE.md**
- Frontend features detailed
- API connection explanation
- Component structure
- Code examples

### 🔗 I want API documentation
→ Read: **backend/API_DOCUMENTATION.md**
- All endpoints listed
- Request/response examples
- Authentication details

---

## 🎨 What's Been Built

### ✅ Fully Functional Frontend
- **7 Complete Pages** with real UI
- **3 Reusable Components** for structure
- **API Integration** with backend
- **Authentication** with JWT tokens
- **Dashboard** with charts and statistics
- **User Management** interface
- **Analytics** and reporting
- **Settings** with multiple sections

### ✅ Backend Integration
- **Proxy Configuration** for API calls
- **JWT Authentication** flow
- **Error Handling** and recovery
- **Token Management** with refresh
- **Protected Routes** for security

### ✅ Startup Scripts
- **startup.bat** - One-click Windows startup
- **startup.ps1** - Advanced PowerShell control
- Both check prerequisites and start everything

---

## 🏗️ Architecture at a Glance

```
Your Browser
    ↓
Frontend (React + Vite) → http://localhost:3000
    ↓
Backend API (FastAPI) → http://localhost:8000
    ↓
Database (PostgreSQL) → localhost:5432
```

**All parts run in Docker containers** (except frontend dev server)

---

## 📦 What You Have

### Frontend Files
```
frontend/
├── src/pages/          → 7 complete page components
├── src/components/     → 3 layout components
├── src/context/        → Authentication state management
├── src/api/           → API client with interceptors
├── vite.config.js     → Build & proxy configuration
├── tailwind.config.js → Styling configuration
├── package.json       → Dependencies list
└── .env               → API connection config
```

### Configuration Files
```
.env                          → Frontend API URL
docker-compose.yml            → Backend services definition
startup.bat                   → Windows startup script
startup.ps1                   → PowerShell startup script
COMPLETE_SETUP_GUIDE.md       → Detailed instructions
QUICK_START_GUIDE.md          → Quick reference
FRONTEND_INTEGRATION_COMPLETE.md → Integration details
```

---

## 🎯 Next Steps

### Step 1: Install Requirements
```
1. Download & Install Docker Desktop
   https://www.docker.com/products/docker-desktop
   
2. Download & Install Node.js (LTS)
   https://nodejs.org/
   
3. RESTART YOUR COMPUTER
```

### Step 2: Start Everything
```powershell
cd "c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main"
.\startup.bat
```

### Step 3: Use the Application
```
Frontend: http://localhost:3000
Backend:  http://localhost:8000/docs
```

---

## 🌟 Features Included

### Dashboard
- Real-time statistics
- Activity charts (line, bar, pie)
- Recent activity feed
- Quick action buttons

### Programs
- Browse all programs
- Search and filter
- Program metrics
- Status tracking

### Analytics
- User engagement metrics
- Program performance
- User progress tracking
- Top performers leaderboard
- Completion breakdown

### Users
- User list with search
- Filter by role
- Completion tracking
- User actions

### Settings
- Account configuration
- Organization details
- Notification preferences
- Security settings

---

## 🛠️ Troubleshooting

### "Port already in use"
```powershell
# Kill the process
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "Docker not found"
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Restart your computer
- Verify: `docker --version`

### "npm not found"
- Install Node.js: https://nodejs.org/
- Restart your computer
- Verify: `npm --version`

### "Can't connect to backend"
```powershell
# Check if services are running
docker-compose ps

# View logs
docker-compose logs app
```

---

## 📊 Quick Reference

| Component | URL | Port |
|-----------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| Database | localhost | 5432 |

---

## 🎓 Learning Path

1. **Start App** → Run `startup.bat`
2. **Login** → Use credentials from backend setup
3. **Explore Dashboard** → See statistics and charts
4. **Create Program** → Add new onboarding program
5. **Check Analytics** → View metrics and progress
6. **Manage Users** → Add/edit user accounts
7. **Configure Settings** → Customize organization

---

## 💾 Command Reference

```powershell
# Start everything
.\startup.bat

# Manual startup
docker-compose up -d        # Start backend
cd frontend && npm run dev   # Start frontend

# Check status
docker-compose ps          # See running containers

# View logs
docker-compose logs -f app  # Follow backend logs
docker-compose logs app -n 50  # Last 50 lines

# Stop everything
docker-compose down        # Stop containers
# (Ctrl+C in frontend terminal)

# Clean restart
docker-compose down -v
docker-compose up -d
cd frontend && npm run dev
```

---

## 🔐 Security Notes

- JWT tokens stored in browser localStorage
- Tokens auto-refresh before expiration
- Invalid tokens trigger re-login
- All API calls require authentication (except login/register)
- HTTPS recommended for production

---

## 📞 Quick Help

### Still confused?
1. Run `startup.bat` - it will guide you
2. Open http://localhost:3000
3. If stuck, check logs: `docker-compose logs -f`

### Want more details?
Read: **COMPLETE_SETUP_GUIDE.md**

### Want API information?
Read: **backend/API_DOCUMENTATION.md**

### Want coding details?
Read: **FRONTEND_INTEGRATION_COMPLETE.md**

---

## ✅ Verification Checklist

Everything working if you can:
- [ ] Run `startup.bat` without errors
- [ ] Access http://localhost:3000 in browser
- [ ] Login with valid credentials
- [ ] See dashboard with charts
- [ ] Navigate to all pages
- [ ] No red errors in browser console

---

## 🎉 You're Ready!

Everything is set up and ready to go. Just run:

```powershell
.\startup.bat
```

Then visit: **http://localhost:3000**

That's it! 🚀

---

**Questions? Check the documentation files listed above or review the logs with `docker-compose logs -f`**
