#!/bin/bash
#
# Automated deployment script for AI Adaptive Onboarding Engine to Railway
# Usage: ./deploy-to-railway.sh -u <github-username> -t <github-token> -k <openai-key>
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
while getopts "u:t:k:s" opt; do
    case $opt in
        u) GITHUB_USERNAME="$OPTARG" ;;
        t) GITHUB_TOKEN="$OPTARG" ;;
        k) OPENAI_KEY="$OPTARG" ;;
        s) SKIP_GIT_PUSH=true ;;
        *) echo "Usage: $0 -u <username> -t <token> -k <openai-key> [-s]"; exit 1 ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AI Adaptive Onboarding Engine - Railway Deployment      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Validate inputs
echo -e "${YELLOW}📋 Validating configuration...${NC}"

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}❌ ERROR: GitHub username is required${NC}"
    echo "Usage: $0 -u <github-username> -t <github-token> -k <openai-key>"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  WARNING: GitHub token not provided. Skipping automated push.${NC}"
    SKIP_GIT_PUSH=true
fi

echo -e "${GREEN}✅ Configuration validated${NC}"
echo ""

# Navigate to project
PROJECT_ROOT="/c/Users/Rajan/OneDrive/Desktop/ai-adaptive-onboarding-engine-main"
echo -e "${YELLOW}📁 Navigating to project: $PROJECT_ROOT${NC}"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ ERROR: Project directory not found${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"
echo -e "${GREEN}✅ Working directory: $(pwd)${NC}"
echo ""

# Initialize Git
echo -e "${YELLOW}🔧 Setting up Git...${NC}"

if [ ! -d ".git" ]; then
    git init
    git config user.email "deployment@railway.app"
    git config user.name "Railway Deployment"
    echo -e "${GREEN}✅ Git initialized${NC}"
else
    echo -e "${GREEN}✅ Git already initialized${NC}"
fi

echo ""

# Push to GitHub (if not skipped)
if [ "$SKIP_GIT_PUSH" != "true" ]; then
    echo -e "${YELLOW}🌐 Setting up GitHub...${NC}"
    
    REPO_NAME="ai-adaptive-onboarding-engine"
    REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REPO_URL"
    
    echo -e "${YELLOW}📝 Committing files...${NC}"
    git add .
    git commit -m "Deploy to Railway: Add configuration" || true
    
    echo -e "${YELLOW}⬆️  Pushing to GitHub...${NC}"
    git branch -M main
    git push -u origin main
    
    echo -e "${GREEN}✅ Code pushed successfully!${NC}"
    echo ""
fi

# Display next steps
echo -e "${YELLOW}🚀 NEXT STEPS:${NC}"
echo ""
echo -e "${BLUE}1. Go to https://railway.app${NC}"
echo -e "${BLUE}2. Sign in with GitHub${NC}"
echo -e "${BLUE}3. Click 'New Project' → 'Deploy from GitHub'${NC}"
echo -e "${BLUE}4. Select: $GITHUB_USERNAME/$REPO_NAME${NC}"
echo -e "${BLUE}5. Click 'Deploy Now'${NC}"
echo ""
echo -e "${BLUE}📚 For detailed instructions, see QUICK_RAILWAY_DEPLOY.md${NC}"
echo ""
