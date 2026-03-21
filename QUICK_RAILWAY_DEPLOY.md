# Quick Railway Deployment (5 minutes)

## TL;DR

This application deploys to Railway in 5 minutes with no credit card required.

### Fast Track Steps:

#### 1. Git Setup (2 min)
```bash
cd c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main
git init
git add .
git commit -m "Initial commit"
```

#### 2. Push to GitHub (2 min)
- Go to https://github.com/new
- Create repo `ai-adaptive-onboarding-engine`
- Copy commands from GitHub and paste them

#### 3. Deploy to Railway (1 min)
- Go to https://railway.app
- Click "New Project"
- Select "Deploy from GitHub"
- Choose your repo
- Click "Deploy Now"

#### 4. Set Environment Variables (5 min)

In Railway dashboard, click "app" service → "Variables":

**Required:**
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<from db service>
POSTGRES_HOST=<from db service>
POSTGRES_PORT=5432
POSTGRES_DB=ai_onboarding
DEBUG=false
JWT_SECRET_KEY=your-random-secret-key-minimum-32-characters-long
```

**Pick ONE LLM (OpenAI recommended for speed):**

OpenAI:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4
```

Gemini:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your-key...
GEMINI_MODEL=gemini-1.5-pro
```

Anthropic:
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...your-key...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### 5. Done! 🎉

- Frontend: Click the URL in Railway dashboard
- API Docs: `https://your-url.railway.app/api/v1/docs`

## Get API Keys

**OpenAI**: https://platform.openai.com/api-keys (5 min)
**Gemini**: https://ai.google.dev (5 min)
**Anthropic**: https://console.anthropic.com (5 min)

## Cost: FREE

Railway free tier covers small apps entirely.

## See Full Guide

→ Read [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed troubleshooting
