# Deployment Guide

## Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git

### Quick Start
```bash
# 1. Clone and setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Start database
docker-compose up -d  # or brew services start postgresql

# 5. Run server
python -m uvicorn app.main:app --reload

# 6. Visit http://localhost:8000/api/v1/docs
```

## Docker Deployment

### Build Docker Image
```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

docker build -t ai-onboarding:latest .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

### Stop Containers
```bash
docker-compose down
```

## Cloud Deployment

### AWS (Elastic Beanstalk)

#### 1. Prepare Application
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p python-3.11 ai-onboarding
```

#### 2. Create `.ebextensions/python.config`
```yaml
option_settings:
  "aws:elasticbeanstalk:container:python:staticfiles":
    /static/: /static/
  "aws:elasticbeanstalk:application:environment":
    PYTHONPATH: /var/app/current:$PYTHONPATH
    DEBUG: "False"
```

#### 3. Create `wsgi.py`
```python
from app.main import app

application = app
```

#### 4. Deploy
```bash
eb create ai-onboarding-env
eb deploy
```

### Azure (Azure App Service)

#### 1. Install Azure CLI
```bash
pip install azure-cli
az login
```

#### 2. Create App Service
```bash
az group create --name ai-onboarding-rg --location eastus

az appservice plan create \
  --name ai-onboarding-plan \
  --resource-group ai-onboarding-rg \
  --sku B2 --is-linux

az webapp create \
  --resource-group ai-onboarding-rg \
  --plan ai-onboarding-plan \
  --name ai-onboarding-app \
  --runtime "PYTHON|3.11"
```

#### 3. Deploy Code
```bash
az webapp up \
  --resource-group ai-onboarding-rg \
  --name ai-onboarding-app
```

### Google Cloud (Cloud Run)

#### 1. Create `requirements.txt` with gunicorn
```
```bash
pip install gunicorn
echo gunicorn >> requirements.txt
```

#### 2. Create `Dockerfile`
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD exec gunicorn --bind :8000 app.main:app
```

#### 3. Deploy
```bash
gcloud run deploy ai-onboarding \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars POSTGRES_HOST=cloudsql
```

## Production Checklist

### Pre-Deployment
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_ORIGINS` in config
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure database credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure domain name
- [ ] Set up error logging (Sentry)
- [ ] Configure monitoring (Datadog, New Relic)
- [ ] Set up backup strategy
- [ ] Test all endpoints
- [ ] Load testing
- [ ] Security audit
- [ ] Add rate limiting
- [ ] Configure CORS properly

### Database Setup
```bash
# Create PostgreSQL user and database
psql -U postgres
CREATE USER onboarding_user WITH PASSWORD 'secure_password';
CREATE DATABASE ai_onboarding OWNER onboarding_user;
GRANT ALL PRIVILEGES ON DATABASE ai_onboarding TO onboarding_user;
```

### Environment Variables
```bash
# .env (production)
DEBUG=False
POSTGRES_USER=onboarding_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=your-database-host
POSTGRES_PORT=5432
POSTGRES_DB=ai_onboarding
LLM_PROVIDER=openai
LLM_API_KEY=your-llm-api-key
```

### WSGI Server (Gunicorn)
```bash
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# With worker class for async
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - run: pip install -r requirements.txt
    
    - run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - uses: azure/webapps-deploy@v2
      with:
        app-name: ai-onboarding
        publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
```

## Monitoring & Logging

### Application Monitoring
```python
# Add to app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Error Tracking
```python
# Sentry integration
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Log Aggregation
```bash
# ELK Stack or Cloud Logging
# Configure logging in config.py
```

## Scaling Strategies

### Horizontal Scaling
1. Load Balancer (Azure LB, AWS ALB, GCP LB)
2. Multiple API instances
3. Shared database
4. Redis cache layer

### Vertical Scaling
1. Increase instance resources
2. Optimize database queries
3. Connection pooling
4. Caching layer

## Backup & Disaster Recovery

### Database Backup
```bash
# Automated backups
pg_dump ai_onboarding > backup.sql

# Restore
psql ai_onboarding < backup.sql
```

### Version Control
- Keep all code in Git
- Tag releases
- Document breaking changes

## Security Hardening

### SSL/TLS
```bash
# Let's Encrypt (Certbot)
certbot certonly --standalone -d yourdomain.com
```

### Firewall Rules
- Restrict database access to app servers
- Restrict API access by region/IP if needed
- Use VPC security groups

### Secrets Management
- Use cloud provider secrets (Azure Key Vault, AWS Secrets Manager)
- Never commit secrets to repo
- Rotate credentials regularly

## Performance Tuning

### Database
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_analysis_user_id ON analyses(user_id);
```

### Application
```python
# Connection pooling settings
pool_size=20
max_overflow=40
pool_recycle=3600
```

### Caching
```bash
# Redis for caching
docker run -d -p 6379:6379 redis:latest
```

## Troubleshooting

### High Memory Usage
```bash
# Check memory
ps aux | grep uvicorn

# Optimize workers
gunicorn -w 2 app.main:app  # Reduce workers
```

### Slow Database Queries
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM analyses WHERE user_id = 1;
```

### Connection Pool Exhaustion
```
Increase pool_size in config.py
Reduce connection timeout
Add connection recycling
```

## Support Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- AWS Documentation: https://aws.amazon.com/documentation/
- Azure Documentation: https://docs.microsoft.com/azure/
- Google Cloud Docs: https://cloud.google.com/docs/
