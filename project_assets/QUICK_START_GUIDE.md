# 🚀 QUICK START - AI Adaptive Onboarding Engine

## Prerequisites Install

### 1. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop
- Install and restart your computer
- Verify: Open PowerShell and run `docker --version`

### 2. Install Node.js (for frontend)
- Download from: https://nodejs.org/ (LTS version recommended)
- Install and restart your computer
- Verify: Open PowerShell and run `node --version`

---

## 🎯 Start the Application

### Option 1: Batch File (Easiest for Windows)
Double-click the file:
```
startup.bat
```

This will:
1. Start the backend (Docker)
2. Install frontend dependencies (if needed)
3. Start the frontend development server
4. Open http://localhost:3000 in your browser

### Option 2: PowerShell Script
Open PowerShell and run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\startup.ps1
```

### Option 3: Manual Steps

**Terminal 1 - Start Backend:**
```powershell
docker-compose up -d
```

**Terminal 2 - Start Frontend:**
```powershell
cd frontend
npm install  # (only needed first time)
npm run dev
```

---

## 📱 Access the Application

Once everything is running:

### Frontend
- **URL:** http://localhost:3000
- **Login:** 
  - Email: `admin@example.com`
  - Password: (as configured in backend)

### Backend API
- **API Docs:** http://localhost:8000/docs (Interactive Swagger UI)
- **API ReDoc:** http://localhost:8000/redoc (Alternative documentation)
- **Health Check:** http://localhost:8000/health

---

## 🎨 Features

### Dashboard
- Statistics cards with trends
- Activity charts
- Recent activities feed

### Programs
- Create and manage onboarding programs
- Search and filter
- Program metrics

### Analytics
- Engagement metrics
- Program performance
- User progress tracking
- Top performers

### Users
- User management
- Completion tracking
- Role management

### Settings
- Account settings
- Organization configuration
- Notifications
- Security

---

## 🛠️ Common Commands

### Check Service Status
```powershell
docker-compose ps
```

### View Backend Logs
```powershell
docker-compose logs -f app
```

### Stop All Services
```powershell
docker-compose down
```

### Clean Rebuild
```powershell
docker-compose down -v
docker-compose up --build -d
```

### Restart Everything
```powershell
docker-compose restart
```

---

## ⚙️ Architecture

```
Browser (localhost:3000)
    ↓
React Frontend (Vite)
    ↓
Axios API Client
    ↓
FastAPI Backend (localhost:8000)
    ↓
PostgreSQL Database (localhost:5432)
```

---

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F
```

### Docker daemon is not running
- Open Docker Desktop
- Wait 30 seconds for it to start
- Try again

### npm: command not found
- Install Node.js from https://nodejs.org/
- Restart your terminal/computer
- Verify: `npm --version`

### Backend won't start
```powershell
# Check logs
docker-compose logs app

# Clean rebuild
docker-compose down -v
docker-compose up --build -d
```

### Frontend shows "Cannot connect to server"
- Verify backend is running: http://localhost:8000/docs
- Check .env file in frontend directory
- Ensure both are on correct ports

---

## 📚 Documentation

For detailed information, see:
- `COMPLETE_SETUP_GUIDE.md` - Full setup instructions
- `backend/API_DOCUMENTATION.md` - API reference
- `backend/ARCHITECTURE.md` - System architecture
- `backend/DEPLOYMENT.md` - Production deployment

---

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Docker services running: `docker-compose ps` shows all healthy
- [ ] Backend responsive: http://localhost:8000/docs loads
- [ ] Frontend dependencies installed: `npm --version` works
- [ ] Frontend running: http://localhost:3000 loads
- [ ] Can login with valid credentials
- [ ] Can navigate between pages
- [ ] No console errors in browser DevTools

---

## 🎉 You're Ready!

Start developing with the AI Adaptive Onboarding Engine!

**Next Steps:**
1. Login to the application
2. Explore the dashboard
3. Create a new program
4. Check the analytics
5. Manage users

Happy coding! 🚀

---

**Need Help?**
- Check logs: `docker-compose logs -f`
- Check API Docs: http://localhost:8000/docs
- Review errors in browser console (F12)
