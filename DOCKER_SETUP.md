# Complete Docker Installation & Setup Guide

## OS-Specific Installation

### Windows

1. **Download Docker Desktop for Windows:**
   - https://www.docker.com/products/docker-desktop/
   - Click "Docker Desktop for Windows"

2. **Install Docker Desktop:**
   - Run the installer
   - Enable WSL 2 (Windows Subsystem for Linux)
   - Complete installation and restart

3. **Verify Installation:**
   ```powershell
   docker --version
   docker-compose --version
   ```

4. **Enable WSL 2 (if not set):**
   ```powershell
   # Run as Administrator
   wsl --install
   ```

### macOS

1. **Install via Homebrew (recommended):**
   ```bash
   brew install docker docker-compose
   ```

   Or download Docker Desktop:
   - https://www.docker.com/products/docker-desktop/

2. **Verify Installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Start Docker Daemon:**
   - For Docker Desktop: Open Docker.app from Applications
   - Via Homebrew: `brew services start colima` (uses Lima VM)

### Linux (Ubuntu/Debian)

1. **Install using Repository:**
   ```bash
   # Update package index
   sudo apt update
   
   # Install Docker
   sudo apt install -y docker.io docker-compose
   
   # Start Docker Service
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Add current user to docker group (optional, no sudo needed)
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Verify Installation:**
   ```bash
   docker --version
   docker-compose --version
   docker run hello-world
   ```

---

## Available Disk Space Check

```powershell
# Windows (PowerShell)
Get-PSDrive C

# macOS/Linux
df -h

# Docker resources should have at least 4GB free
```

---

## Network Ports Check

### Windows/macOS (PowerShell/Bash)

```bash
# Check if port 5432 is available (PostgreSQL)
netstat -an | grep 5432

# Check if port 8000 is available (App)
netstat -an | grep 8000

# Or use:
lsof -i :5432
lsof -i :8000
```

### Stop Existing Services

```bash
# Kill process on port 5432
# Windows:
Get-Process | Where-Object {$_.Id -eq XXXX} | Stop-Process

# macOS/Linux:
kill -9 $(lsof -t -i:5432)
```

---

## Docker Desktop Settings

### Recommended Configuration

**Windows/macOS:**
1. Open Docker Desktop
2. Settings → Resources
3. Set:
   - CPUs: 4 (or more if available)
   - Memory: 4GB or more
   - Disk: At least 20GB free

**Linux:** 
- Docker uses host resources directly

### Memory Troubleshooting

If you get "Out of Memory" errors:

```bash
# Increase memory in docker-compose.yml:
# Under services > app > deploy > resources > limits > memory
# Change to: 4G or 8G
```

---

## First Time Setup

### 1. Clone or Download Project

```bash
cd ai-adaptive-onboarding-engine-main
```

### 2. Create .env File

```bash
# Copy example (if Windows, use PowerShell)
cp backend/.env.example backend/.env

# Or manually create backend/.env with:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=ai_onboarding
APP_ENV=development
DEBUG=true
```

### 3. Build Docker Image (Optional)

```bash
# Pre-build image (usually happens automatically)
docker-compose build
```

This downloads base images and installs dependencies (takes 2-3 minutes first time).

### 4. Start Services

```bash
docker-compose up -d
```

Waits on first start (database initialization):
1. Database container starts
2. Database initializes tables
3. App container starts
4. App waits for database health check
5. App starts FastAPI server

Total time: ~30 seconds to 1 minute

### 5. Verify Everything Works

```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs app

# Test API
curl http://localhost:8000/docs
# Or open browser: http://localhost:8000/docs
```

---

## Common Docker Commands

### Container Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View running services
docker-compose ps

# View all services (including stopped)
docker-compose ps -a
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow app logs
docker-compose logs -f app

# Last 100 lines of app logs
docker-compose logs -f --tail=100 app

# Logs from specific time
docker-compose logs --since 10m app
```

### Execute Commands

```bash
# Run command in app container
docker-compose exec app bash
docker-compose exec app python --version

# Run command in database container
docker-compose exec db psql -U postgres -d ai_onboarding
```

### Rebuild

```bash
# Rebuild app image (use after updating requirements.txt)
docker-compose build app

# Rebuild everything
docker-compose build

# Rebuild and start
docker-compose up --build -d
```

### Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove all containers and volumes (DELETE DATA!)
docker-compose down -v

# Remove unused images
docker image prune

# Remove all unused resources
docker system prune -a
```

---

## Troubleshooting Docker

### Docker Daemon Not Running

```bash
# macOS/Linux:
sudo systemctl start docker

# Or open Docker Desktop application

# Or with Homebrew on macOS:
brew services start colima
```

### Cannot Connect to Docker Daemon

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo docker-compose up -d
```

### Port Already in Use

```bash
# Find what's using port
lsof -i :8000
lsof -i :5432

# Or use Docker to find container
docker ps

# Stop conflicting container
docker stop <container_name>

# Or use different ports in docker-compose.yml
# Change ports: "9000:8000" for different host port
```

### Database Connection Timeout

```bash
# Check database is healthy
docker-compose ps db
# Status should say "Up (healthy)"

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Or start fresh
docker-compose down -v
docker-compose up -d
```

### Out of Memory Errors

```bash
# Increase Docker memory:
# Windows/macOS: Docker Desktop Settings → Resources

# Or limit in docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 8G  # Increase to available RAM
```

### App Keeps Crashing

```bash
# Check app logs
docker-compose logs app

# Check Python errors
docker-compose logs app | grep -i error

# Rebuild app
docker-compose build app

# Restart
docker-compose restart app
```

---

## Performance Tips

### Local Development

```bash
# Exclude large directories from bind mount volume
# In docker-compose.yml, add:
volumes:
  - ./backend:/app
  - /app/__pycache__     # Exclude
  - /app/.pytest_cache   # Exclude
  - /app/node_modules    # Exclude
```

### Database Performance

```bash
# Create indexes for custom queries
docker-compose exec db psql -U postgres -d ai_onboarding

# Inside psql:
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
ANALYZE users;
```

### Monitor Resource Usage

```bash
# Real-time resource stats
docker stats

# Or specific container
docker stats ai-onboarding-app ai-onboarding-db
```

---

## Backup Before Major Changes

```bash
# Create backup
docker-compose exec db bash /scripts/backup.sh /backups

# Verify backup
ls -lh backups/

# Stop services safely
docker-compose down

# Make changes...

# Restore if needed
docker-compose up -d
docker-compose exec db bash /scripts/restore.sh /backups/db_backup_TIMESTAMP.sql.gz
```

---

## Next Steps

1. **Follow Docker Quick Start:** See `DOCKER_QUICKSTART.md`
2. **Test API:** http://localhost:8000/docs
3. **Read Full Documentation:** See `PHASE_2_DATABASE.md`
4. **Deploy to Production:** Configure environment accordingly

---

**Docker is now ready for your AI Adaptive Onboarding Engine!**
