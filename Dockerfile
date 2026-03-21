FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend directory
COPY backend/ backend/
WORKDIR /backend

# Create necessary directories
RUN mkdir -p uploads logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV DEBUG=false

# Run migrations and start the app
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
