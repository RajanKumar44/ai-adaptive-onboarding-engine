# Complete Docker cleanup and rebuild script for PowerShell

Write-Host "========================================" -ForegroundColor Green
Write-Host "COMPLETE DOCKER CLEANUP & REBUILD" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Step 1: Kill all containers
Write-Host "`n[1/8] Stopping containers..." -ForegroundColor Yellow
$containers = docker ps -q 2>$null
if ($containers) {
    docker kill $containers 2>$null
    Start-Sleep -Seconds 2
} else {
    Write-Host "No containers running"
}

# Step 2: Remove all containers
Write-Host "`n[2/8] Removing containers..." -ForegroundColor Yellow
$allContainers = docker ps -aq 2>$null
if ($allContainers) {
    docker rm $allContainers 2>$null
    Start-Sleep -Seconds 2
} else {
    Write-Host "No containers to remove"
}

# Step 3: Remove all images
Write-Host "`n[3/8] Removing images..." -ForegroundColor Yellow
$images = docker images -q 2>$null
if ($images) {
    docker rmi -f $images 2>$null
    Start-Sleep -Seconds 2
} else {
    Write-Host "No images to remove"
}

# Step 4: Remove volumes
Write-Host "`n[4/8] Removing volumes..." -ForegroundColor Yellow
docker volume prune -f 2>$null
Start-Sleep -Seconds 2

# Step 5: System cleanup
Write-Host "`n[5/8] System cleanup..." -ForegroundColor Yellow
docker system prune -a -f --volumes 2>$null
Start-Sleep -Seconds 2

# Step 6: Navigate to backend
Write-Host "`n[6/8] Navigating to backend directory..." -ForegroundColor Yellow
cd c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main\backend
Write-Host "Current directory: $(Get-Location)"

# Step 7: Build from scratch
Write-Host "`n[7/8] Building containers from scratch..." -ForegroundColor Yellow
docker-compose build --no-cache
Write-Host "Build complete!" -ForegroundColor Green

# Step 8: Start containers
Write-Host "`n[8/8] Starting containers..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "Containers starting..." -ForegroundColor Green

# Wait for initialization
Write-Host "`nWaiting 40 seconds for services to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 40

# Show status
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "CONTAINER STATUS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
docker ps

# Show logs
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "APPLICATION LOGS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
docker logs ai-onboarding-app --tail 100

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "REBUILD COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
