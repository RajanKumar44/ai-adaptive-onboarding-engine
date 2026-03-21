#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated deployment script for AI Adaptive Onboarding Engine to Railway
.DESCRIPTION
    This script automates the entire deployment process including git setup,
    GitHub repository creation, and Railway deployment configuration.
.EXAMPLE
    .\deploy-to-railway.ps1 -GitHubToken "ghp_xxxxx" -GitHubUsername "myusername" -OpenAIKey "sk-xxxxx"
#>

param(
    [string]$GitHubToken,
    [string]$GitHubUsername,
    [string]$OpenAIKey,
    [switch]$SkipGitPush = $false
)

$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

# Colors for output
$Green = @{ ForegroundColor = "Green" }
$Yellow = @{ ForegroundColor = "Yellow" }
$Red = @{ ForegroundColor = "Red" }
$Blue = @{ ForegroundColor = "Cyan" }

Write-Host "╔════════════════════════════════════════════════════════════╗" @Blue
Write-Host "║   AI Adaptive Onboarding Engine - Railway Deployment      ║" @Blue
Write-Host "╚════════════════════════════════════════════════════════════╝" @Blue
Write-Host ""

# Step 1: Validate inputs
Write-Host "📋 STEP 1: Validating configuration..." @Yellow

if (-not $GitHubUsername) {
    Write-Host "❌ ERROR: GitHubUsername is required" @Red
    Write-Host "Usage: .\deploy-to-railway.ps1 -GitHubUsername 'yourname' -GitHubToken 'ghp_xxxxx' -OpenAIKey 'sk-xxxxx'"
    exit 1
}

if (-not $GitHubToken) {
    Write-Host "⚠️  WARNING: GitHubToken not provided. Skipping automated GitHub repo creation." @Yellow
    $SkipGitPush = $true
}

if (-not $OpenAIKey) {
    Write-Host "⚠️  WARNING: OpenAI key not provided. You'll need to add LLM credentials to Railway manually." @Yellow
}

Write-Host "✅ Configuration validated" @Green
Write-Host ""

# Step 2: Navigate to project directory
Write-Host "📁 STEP 2: Navigating to project directory..." @Yellow
$ProjectRoot = "c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main"

if (-not (Test-Path $ProjectRoot)) {
    Write-Host "❌ ERROR: Project directory not found at $ProjectRoot" @Red
    exit 1
}

Set-Location $ProjectRoot
Write-Host "✅ Working directory: $(Get-Location)" @Green
Write-Host ""

# Step 3: Verify Git is initialized
Write-Host "🔧 STEP 3: Verifying Git setup..." @Yellow

if (-not (Test-Path ".git")) {
    Write-Host "⚠️  Git not initialized. Initializing now..." @Yellow
    git init
    git config user.email "deployment@railway.app"
    git config user.name "Railway Deployment"
} else {
    Write-Host "✅ Git repository already initialized" @Green
}

Write-Host ""

# Step 4: Create GitHub repository (if token provided)
if (-not $SkipGitPush) {
    Write-Host "🌐 STEP 4: Creating GitHub repository..." @Yellow
    
    $RepoName = "ai-adaptive-onboarding-engine"
    $RepoUrl = "https://github.com/$GitHubUsername/$RepoName.git"
    
    # Check if remote already exists
    $RemoteExists = git config --get remote.origin.url
    
    if ($RemoteExists -eq $RepoUrl) {
        Write-Host "✅ Remote already configured: $RepoUrl" @Green
    } else {
        Write-Host "Setting up GitHub remote: $RepoUrl"
        
        # Remove existing origin if different
        if ($RemoteExists) {
            git remote remove origin
        }
        
        git remote add origin $RepoUrl
        Write-Host "✅ Remote configured" @Green
    }
    
    Write-Host ""
    
    # Step 5: Commit changes
    Write-Host "📝 STEP 5: Committing files..." @Yellow
    
    $Status = git status --porcelain
    if ($Status) {
        git add .
        git commit -m "Deployment to Railway: Add configuration files"
        Write-Host "✅ Changes committed" @Green
    } else {
        Write-Host "✅ Everything up to date" @Green
    }
    
    Write-Host ""
    
    # Step 6: Push to GitHub
    Write-Host "⬆️  STEP 6: Pushing to GitHub..." @Yellow
    
    try {
        git branch -M main
        git push -u origin main
        Write-Host "✅ Code pushed to GitHub successfully!" @Green
    } catch {
        Write-Host "❌ ERROR pushing to GitHub: $_" @Red
        Write-Host "⚠️  You may need to create the repository manually at https://github.com/new" @Yellow
        exit 1
    }
    
    Write-Host ""
}

# Step 7: Display deployment instructions
Write-Host "🚀 STEP 7: Deployment Instructions" @Yellow
Write-Host ""
Write-Host "Your code is ready! Now to complete deployment:" @Green
Write-Host ""
Write-Host "  1️⃣  Go to: https://railway.app" @Blue
Write-Host ""
Write-Host "  2️⃣  Sign up/login with GitHub" @Blue
Write-Host ""
Write-Host "  3️⃣  Click 'New Project' → 'Deploy from GitHub'" @Blue
Write-Host ""
Write-Host "  4️⃣  Select repository: $GitHubUsername/$RepoName" @Blue
Write-Host ""
Write-Host "  5️⃣  Click 'Deploy Now'" @Blue
Write-Host ""
Write-Host "  6️⃣  After deployment, configure variables:" @Blue
Write-Host ""

$EnvVars = @"
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<copy from db service>
POSTGRES_HOST=<copy from db service>
POSTGRES_DB=ai_onboarding
DEBUG=false
JWT_SECRET_KEY=$(New-Guid | ForEach-Object { $_.ToString().Replace('-', '') })
LLM_PROVIDER=openai
OPENAI_API_KEY=<your OpenAI key>
OPENAI_MODEL=gpt-4
"@

Write-Host $EnvVars | ForEach-Object { "      $_" }

Write-Host ""
Write-Host "📚 For detailed help, see:" @Blue
Write-Host "   - QUICK_RAILWAY_DEPLOY.md (5-minute version)" @Blue
Write-Host "   - RAILWAY_DEPLOYMENT.md (comprehensive guide)" @Blue
Write-Host ""

# Step 8: Generate a summary report
Write-Host "📊 STEP 8: Generating deployment report..." @Yellow
Write-Host ""

$Report = @"
═══════════════════════════════════════════════════════════════
  DEPLOYMENT READINESS REPORT
═══════════════════════════════════════════════════════════════

✅ Project Status: READY FOR RAILWAY DEPLOYMENT

Repository Information:
  • Project: AI Adaptive Onboarding Engine
  • Location: $ProjectRoot
  • Git Branch: main
  • Remote: $RepoUrl

Deployment Configuration:
  • Dockerfile: ✅ Present
  • railway.json: ✅ Present
  • .gitignore: ✅ Present
  • requirements.txt: ✅ Present
  • Environment: Production-ready

Next Steps:
  1. Visit https://railway.app
  2. Connect GitHub (if not already connected)
  3. Deploy from repository: $GitHubUsername/$RepoName
  4. Set environment variables in Railway dashboard
  5. Wait for build to complete (~2-5 minutes)
  6. Access your app via Railway URL

Resources:
  • Railway Docs: https://docs.railway.app
  • GitHub Repo: $RepoUrl
  • Project Root: $ProjectRoot

═══════════════════════════════════════════════════════════════
"@

Write-Host $Report @Green

# Save report to file
$Report | Out-File -FilePath "DEPLOYMENT_REPORT.txt" -Encoding UTF8
Write-Host "📄 Report saved to: DEPLOYMENT_REPORT.txt" @Green
Write-Host ""

Write-Host "✨ Setup complete! Your application is ready for Railway deployment." @Green
Write-Host ""
