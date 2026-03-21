@echo off
:: AI Adaptive Onboarding Engine - Quick Start Batch Script
:: Run this file to start the entire application

setlocal enabledelayedexpansion
title AI Adaptive Onboarding Engine - Startup

echo.
echo ================================
echo AI Adaptive Onboarding Engine
echo Quick Start Script
echo ================================
echo.

:: Check if Docker is installed
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker found

:: Check if Docker Compose is installed
echo Checking Docker Compose installation...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not installed
    pause
    exit /b 1
)
echo [OK] Docker Compose found

echo.
echo ========================================
echo Starting Backend Services (Docker)
echo ========================================
echo.

:: Stop existing containers
echo Stopping existing containers...
docker-compose down 2>nul

:: Start services
echo Starting Docker containers...
echo This may take 15-20 seconds...
docker-compose up -d

if errorlevel 1 (
    echo ERROR: Failed to start Docker containers
    pause
    exit /b 1
)

echo.
echo Waiting for services to be ready...
timeout /t 5 /nobreak

echo.
echo [OK] Backend services started!
echo.
echo ========================================
echo Service URLs
echo ========================================
echo Frontend:        http://localhost:3000 (once started)
echo Backend API:     http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo API ReDoc:       http://localhost:8000/redoc
echo.

:: Check if Node.js is installed
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js is not installed
    echo Frontend will not start automatically
    echo Install Node.js from https://nodejs.org/
    echo.
    echo Backend is running at http://localhost:8000/docs
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo [OK] Node.js found

echo.
echo ========================================
echo Starting Frontend Development Server
echo ========================================
echo.

cd frontend

:: Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    echo This may take 2-5 minutes...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo [OK] Starting development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the development server
echo.

call npm run dev

cd ..

:: Script finished
echo.
echo Development server stopped.
pause
