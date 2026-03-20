# -------------------------------

# Stage 1: Builder

# -------------------------------

FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements

COPY requirements.txt .

# Create virtual environment and install dependencies

RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# -------------------------------

# Stage 2: Runtime

# -------------------------------

FROM python:3.11-slim

WORKDIR /app

# Environment variables

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder

COPY --from=builder /opt/venv /opt/venv

# Copy application code

COPY . .

# Ensure directories exist

RUN mkdir -p /app/uploads

# Copy and set permissions for entrypoint

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create non-root user

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port

EXPOSE 8000

# Health check (safe endpoint)

HEALTHCHECK CMD curl -f http://localhost:8000/docs || exit 1

# Start application

ENTRYPOINT ["/app/entrypoint.sh"]
