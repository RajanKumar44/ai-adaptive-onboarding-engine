#!/usr/bin/env powershell
# AI Adaptive Onboarding Engine - Complete Startup Script
# This script starts both the backend (Docker) and frontend (npm dev server)

param(
    [string]$Action = "start",  # start, stop, restart, logs, status
    [switch]$Interactive = $false
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommandPath

Write-Host "================================" -ForegroundColor Cyan
Write-Host "AI Adaptive Onboarding Engine" -ForegroundColor Cyan
Write-Host "Startup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Helper function for colored output
function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "[ $Message ]" -ForegroundColor Green -BackgroundColor Black
    Write-Host ""
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ ERROR: $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  WARNING: $Message" -ForegroundColor Yellow
}

# Check prerequisites
function Check-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    $allChecked = $true
    
    # Check Docker
    Write-Info "Checking Docker..."
    try {
        $dockerVersion = docker --version 2>&1
        Write-Success "Docker: $dockerVersion"
    } catch {
        Write-Error-Custom "Docker not found. Please install Docker Desktop."
        $allChecked = $false
    }
    
    # Check Docker Compose
    Write-Info "Checking Docker Compose..."
    try {
        $composeVersion = docker-compose --version 2>&1
        Write-Success "Docker Compose: $composeVersion"
    } catch {
        Write-Error-Custom "Docker Compose not found."
        $allChecked = $false
    }
    
    # Check Node.js (for frontend)
    Write-Info "Checking Node.js..."
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js: $nodeVersion"
    } catch {
        Write-Warning-Custom "Node.js not found. Frontend will not work. Install from https://nodejs.org/"
        $allChecked = $false
    }
    
    # Check npm
    Write-Info "Checking npm..."
    try {
        $npmVersion = npm --version 2>&1
        Write-Success "npm: $npmVersion"
    } catch {
        Write-Warning-Custom "npm not found. Frontend will not work."
        $allChecked = $false
    }
    
    if (-not $allChecked) {
        Write-Error-Custom "Some prerequisites are missing. Please install them before continuing."
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Success "All prerequisites found!"
}

# Start services
function Start-Services {
    Write-Header "Starting Services"
    
    Push-Location $projectRoot
    
    # Start backend
    Write-Info "Starting backend services (Docker)..."
    Write-Info "This may take 15-20 seconds..."
    
    docker-compose down 2>&1 | Out-Null
    docker-compose up -d 2>&1 | Out-Null
    
    # Check if services started
    $attempts = 0
    $maxAttempts = 30
    $backendReady = $false
    
    while ($attempts -lt $maxAttempts) {
        $status = docker-compose ps 2>&1
        if ($status -like "*Up*" -and $status -like "*ai-onboarding-app*") {
            Write-Success "Backend services started!"
            $backendReady = $true
            break
        }
        $attempts++
        Start-Sleep -Seconds 1
        Write-Host -NoNewline "."
    }
    
    if (-not $backendReady) {
        Write-Error-Custom "Backend failed to start. Checking logs..."
        docker-compose logs app
        exit 1
    }
    
    Write-Success "Backend is running on http://localhost:8000"
    Write-Success "Backend API Docs: http://localhost:8000/docs"
    
    # Start frontend if Node.js is available
    Write-Info "Checking if frontend can be started..."
    try {
        $npmVersion = npm --version 2>&1
        
        Write-Info "Installing frontend dependencies (if needed)..."
        Push-Location "$projectRoot\frontend"
        
        if (-not (Test-Path "node_modules")) {
            Write-Info "node_modules not found. Installing packages..."
            npm install 2>&1 | Out-Null
            Write-Success "Frontend dependencies installed"
        } else {
            Write-Info "Frontend dependencies already installed"
        }
        
        Write-Host ""
        Write-Header "Starting Frontend Development Server"
        Write-Info "Frontend will start on http://localhost:3000"
        Write-Info "Press Ctrl+C to stop the development server"
        Write-Host ""
        
        npm run dev
        
    } catch {
        Write-Error-Custom "Could not start frontend: $_"
        Write-Info "Backend is still running on http://localhost:8000"
        Write-Info "You can access the API documentation: http://localhost:8000/docs"
        Pop-Location
    }
    
    Pop-Location
}

# Stop services
function Stop-Services {
    Write-Header "Stopping Services"
    
    Push-Location $projectRoot
    
    Write-Info "Stopping Docker containers..."
    docker-compose down 2>&1 | Out-Null
    
    Write-Success "Services stopped"
    Pop-Location
}

# Show status
function Show-Status {
    Write-Header "Service Status"
    
    Push-Location $projectRoot
    
    $status = docker-compose ps 2>&1
    Write-Host $status
    
    Write-Host ""
    Write-Info "Frontend: http://localhost:3000"
    Write-Info "Backend: http://localhost:8000"
    Write-Info "API Docs: http://localhost:8000/docs"
    
    Pop-Location
}

# Show logs
function Show-Logs {
    Write-Header "Service Logs"
    
    Push-Location $projectRoot
    
    Write-Info "Showing last 50 lines of logs. Press Ctrl+C to stop."
    Write-Info ""
    
    docker-compose logs --tail=50 -f
    
    Pop-Location
}

# Main execution
switch ($Action.ToLower()) {
    "check" {
        Check-Prerequisites
    }
    "start" {
        Check-Prerequisites
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Write-Info "Restarting services..."
        Stop-Services
        Start-Sleep -Seconds 2
        Start-Services
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    default {
        Write-Host ""
        Write-Host "Usage: .\startup.ps1 [action]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Cyan
        Write-Host "  start      - Start all services (default)" -ForegroundColor White
        Write-Host "  stop       - Stop all services" -ForegroundColor White
        Write-Host "  restart    - Restart all services" -ForegroundColor White
        Write-Host "  status     - Show current service status" -ForegroundColor White
        Write-Host "  logs       - Show service logs (follow mode)" -ForegroundColor White
        Write-Host "  check      - Check prerequisites only" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  .\startup.ps1 start" -ForegroundColor Gray
        Write-Host "  .\startup.ps1 logs" -ForegroundColor Gray
        Write-Host "  .\startup.ps1 status" -ForegroundColor Gray
        Write-Host ""
    }
}
