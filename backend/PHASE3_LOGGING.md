# PHASE 3: LOGGING & MONITORING IMPLEMENTATION

## 📊 Overview

Complete logging, monitoring, and error tracking system with:
- **Structured Logging** - JSON and colored console logs with context
- **Log Aggregation** - Centralized file-based logging with rotation
- **Application Monitoring** - Prometheus metrics for infrastructure monitoring
- **Error Tracking** - Sentry integration for error analysis
- **Request/Response Logging** - Detailed HTTP transaction logging
- **Performance Profiling** - Function-level timing and memory tracking

---

## ✅ Implementation Status

| Component | Status | Lines of Code |
|-----------|--------|----------------|
| Structured Logging Module | ✓ Complete | 280+ |
| Request/Response Logging Middleware | ✓ Complete | 240+ |
| Error Tracking (Sentry) Integration | ✓ Complete | 220+ |
| Prometheus Metrics Collection | ✓ Complete | 240+ |
| Prometheus Middleware | ✓ Complete | 150+ |
| Performance Profiling Tools | ✓ Complete | 280+ |
| Metrics Routes/Endpoints | ✓ Complete | 240+ |
| Config Integration | ✓ Complete | 40+ |
| Main.py Integration | ✓ Complete | 100+ |
| Documentation | ✓ Complete | This file |
| **TOTAL** | **✓ COMPLETE** | **1,780+** |

---

## 🏗️ Architecture

### Logging Stack

```
┌─────────────────────────────────────────────────────────┐
│         Application Code (Routes, Services)             │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│              Logging Module (logging_config.py)          │
│  - Structured JSON formatting                           │
│  - Colored console output                               │
│  - File rotation and archival                           │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼────┐    ┌───▼────┐    ┌───▼────┐
    │ Console│    │ App Log │    │ Error  │
    │ (Dev)  │    │ (JSON)  │    │ Log    │
    └────────┘    └────────┘    └────────┘
```

### Monitoring Stack

```
┌──────────────────────────────────────────────────────────┐
│  Application Routes (Auth, Analysis, Admin)             │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────┴───────────────────────────────────────────┐
│           Middleware Stack (in order)                    │
│                                                          │
│  1. Error Logging Middleware                            │
│  2. Request ID Middleware                               │
│  3. Structured Logging Middleware                       │
│  4. Performance Metrics Middleware                      │
│  5. Prometheus Metrics Middleware                       │
│  6. Metrics Recorder Middleware                         │
└──────────────┬───────────────────────────────────────────┘
               │
        ┌──────┴──────┬────────┬──────────┐
        │             │        │          │
    ┌───▼───┐    ┌───▼──┐ ┌──▼──┐   ┌──▼─┐
    │Logging│    │Sentry│ │Prom │   │Prof│
    │Files  │    │Cloud │ │etheus│   │ile │
    └───────┘    └──────┘ └─────┘   └────┘
```

---

## 📁 New Files Created

### 1. **app/core/logging_config.py** (280 lines)

Structured logging configuration with JSON and colored output.

```python
from app.core.logging_config import (
    LoggerManager,
    PerformanceTimer,
    log_performance,
    log_function_call,
    logger
)

# Initialize logging
LoggerManager.initialize("logs")

# Get logger instance
app_logger = LoggerManager.get_logger("my_module")

# Use performance timer
with PerformanceTimer("my_operation"):
    # Perform operation
    pass

# Use decorator
@log_performance("my_function")
async def my_async_function():
    pass

@log_function_call()
def my_sync_function():
    pass
```

**Key Classes:**
- `LoggerManager` - Centralized logging setup
- `StructuredFormatter` - Custom JSON formatter
- `PerformanceTimer` - Context manager for timing
- `log_performance()` - Decorator for function timing
- `log_function_call()` - Decorator for call tracing

### 2. **app/middleware/logging_middleware.py** (240 lines)

Request/response logging and performance tracking middleware.

**Key Middleware Classes:**
- `RequestIDMiddleware` - Adds unique request ID for tracing
- `StructuredLoggingMiddleware` - Logs all requests/responses with timing
- `PerformanceMetricsMiddleware` - Tracks endpoint performance statistics
- `ErrorLoggingMiddleware` - Detailed error logging with context

**Features:**
- Request ID generation and propagation
- Request/response timing
- Error tracking with stack traces
- Performance metrics by endpoint category
- Sensitive header redaction
- User identification (when authenticated)

### 3. **app/core/sentry_config.py** (220 lines)

Error tracking and monitoring with Sentry.

```python
from app.core.sentry_config import (
    SentryManager,
    setup_sentry_middleware
)

# Initialize Sentry
SentryManager.initialize()

# Setup middleware
setup_sentry_middleware(app)

# Capture exceptions
SentryManager.capture_exception(exception)

# Track user context
SentryManager.set_user_context(user_id="123", role="admin")

# Add breadcrumbs
SentryManager.add_breadcrumb("User logged in", category="auth")
```

**Key Features:**
- Automatic exception tracking
- Performance monitoring (transactions)
- User context tracking
- Breadcrumb trail for debugging
- Configurable filtering
- Release and environment tagging

### 4. **app/core/prometheus_config.py** (240 lines)

Prometheus metrics collection for infrastructure monitoring.

```python
from app.core.prometheus_config import PrometheusMetrics

# Record request
PrometheusMetrics.record_request(
    method="GET",
    endpoint="/api/analyze",
    status=200,
    duration=0.123,
    response_size=1024
)

# Record database query
PrometheusMetrics.record_db_query(
    operation="SELECT",
    table="users",
    duration=0.050
)

# Record error
PrometheusMetrics.record_error("ValueError", "/api/analyze")

# Get metrics in Prometheus format
metrics_text = PrometheusMetrics.get_metrics_text()
```

**Metrics Collected:**
- HTTP request count (by method, endpoint, status)
- HTTP request latency (histogram with buckets)
- Response size (by endpoint)
- Database query count (by operation, table)
- Database query latency
- Error counts (by type, endpoint)
- Login attempts (success/failure)
- Analysis count (by skill category)
- Rate limited requests
- Active sessions

### 5. **app/middleware/prometheus_middleware.py** (150 lines)

Middleware for automatic Prometheus metrics collection.

**Key Middleware:**
- `PrometheusMetricsMiddleware` - Automatic metric recording for HTTP requests
- `MetricsRecorderMiddleware` - Records specific application events
- `DatabaseMetricsMiddleware` - Integrates with SQLAlchemy for DB metrics

### 6. **app/core/performance.py** (280 lines)

Function-level performance profiling and analysis.

```python
from app.core.performance import (
    performance_profiler,
    profile_function,
    get_profiling_summary,
    reset_profiling
)

# Using decorator
@profile_function("my_operation")
async def my_function():
    pass

# Get summary
summary = get_profiling_summary()
print(summary["performance"]["my_operation"])

# Export to CSV
performance_profiler.export_csv("profiling_data.csv")
```

**Profilers:**
- `PerformanceProfiler` - Function call timing and success rates
- `MemoryProfiler` - Memory allocation tracking
- `RequestProfiler` - Request-level performance tracking

### 7. **app/routes/metrics_routes.py** (240 lines)

Monitoring and metrics API endpoints.

**Endpoints:**
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/metrics/prometheus` | GET | Admin | Prometheus format metrics |
| `/api/v1/metrics/health` | GET | None | Application health check |
| `/api/v1/metrics/performance` | GET | Admin | Function profiling data |
| `/api/v1/metrics/performance/reset` | POST | Admin | Clear profiling data |
| `/api/v1/metrics/endpoints` | GET | Admin | Endpoint performance stats |
| `/api/v1/metrics/summary` | GET | Admin | Overall metrics summary |
| `/api/v1/metrics/logs-info` | GET | Admin | Logging configuration |
| `/api/v1/metrics/sentry-info` | GET | Admin | Sentry configuration |
| `/api/v1/metrics/status` | GET | None | Monitoring system status |

---

## 🔧 Configuration

### Logging Configuration (app/core/config.py)

```python
# Environment
ENVIRONMENT = development|staging|production
LOG_LEVEL = DEBUG|INFO|WARNING|ERROR|CRITICAL
LOG_FORMAT = colored|json

# File Logging
LOG_DIR = ./logs
LOG_MAX_BYTES = 104857600  # 100MB
LOG_BACKUP_COUNT = 10      # Keep 10 backups

# Request/Response Logging
LOG_REQUESTS_ENABLED = True
LOG_RESPONSES_ENABLED = True
LOG_REQUEST_BODY_ENABLED = False  # Sensitive data
LOG_RESPONSE_BODY_ENABLED = False # Sensitive data

# Sentry Configuration
SENTRY_DSN = https://key@sentry.io/project  # Leave empty to disable
SENTRY_TRACES_SAMPLE_RATE = 0.1             # 10% of traces
SENTRY_PROFILES_SAMPLE_RATE = 0.1           # 10% of profiles

# Prometheus Configuration  
PROMETHEUS_ENABLED = True
PROMETHEUS_PORT = 8001

# Performance Profiling
PROFILING_ENABLED = False  # Adds overhead
PROFILING_SAMPLE_RATE = 0.1
SLOW_QUERY_THRESHOLD_MS = 1000
```

### .env.example Configuration

See `.env.example` for complete configuration options with comments.

```bash
# Copy example
cp .env.example .env

# Update for your environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_FORMAT=colored
SENTRY_DSN=  # Leave empty for local development
PROMETHEUS_ENABLED=True
```

---

## 📈 Middleware Stack Order (Important!)

The order of middleware is critical for proper request processing:

```
1. ErrorLoggingMiddleware          - Catches unhandled errors
2. RequestIDMiddleware              - Generates request ID
3. StructuredLoggingMiddleware      - Logs requests/responses
4. PerformanceMetricsMiddleware     - Tracks endpoint performance
5. PrometheusMetricsMiddleware      - Collects Prometheus metrics
6. MetricsRecorderMiddleware        - Records app-specific events
7. RateLimiter Exception Handler    - Rate limit handling
8. CORSMiddleware                   - CORS validation
9. TrustedHostMiddleware            - Host validation
10. Sentry Middleware (auto-added)  - Error tracking
```

Each middleware can add headers, context, and track metrics.

---

## 🎯 Logging Examples

### Using Logger Directly

```python
from app.core.logging_config import logger

# Simple log
logger.info("User logged in successfully")

# With context
logger.warning(
    "High latency detected",
    extra={
        "endpoint": "/api/analyze",
        "duration_ms": 5000,
        "user_id": "123"
    }
)

# Error with stack trace
try:
    process_data()
except Exception as e:
    logger.error(
        "Failed to process data",
        extra={"error_type": type(e).__name__},
        exc_info=True  # Includes stack trace
    )
```

### Using Decorators

```python
from app.core.logging_config import log_performance, log_function_call

@log_performance("data_processing")  # Logs timing
async def process_data(user_id: int):
    await service.analyze(user_id)

@log_function_call(logging.DEBUG)      # Logs function calls
def validate_email(email: str) -> bool:
    return "@" in email
```

### Using Context Manager

```python
from app.core.logging_config import PerformanceTimer

with PerformanceTimer("batch_operation") as timer:
    for i in range(1000):
        perform_operation(i)
    
    # Access elapsed time
    elapsed_ms = timer.get_elapsed_ms()
```

---

## 🔍 Monitoring & Error Tracking

### Prometheus Metrics Collection

Metrics are automatically collected by middleware:

```bash
# Get all metrics
curl http://localhost:8000/api/v1/metrics/prometheus

# Common metrics by endpoint
http_requests_total{method="POST",endpoint="/api/v1/analyze",status="200"}
http_request_duration_seconds{method="GET",endpoint="/api/v1/auth/me"}
db_queries_total{operation="SELECT",table="users"}
errors_total{error_type="ValueError",endpoint="/api/v1/analyze"}
```

### Using Prometheus with Queries

```ini
# Prometheus scrape config
global:
  scrape_interval: 15s
  
scrape_configs:
  - job_name: 'onboarding-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics/prometheus'
```

### Prometheus Query Examples

```promql
# Request rate (requests/second)
rate(http_requests_total[5m])

# Average latency by endpoint
avg(rate(http_request_duration_seconds_sum[5m])) / 
    avg(rate(http_request_duration_seconds_count[5m]))

# Error rate by endpoint
rate(errors_total[5m]) / rate(http_requests_total[5m])

# Database query latency (95th percentile)
histogram_quantile(0.95, http_request_duration_seconds)
```

### Sentry Error Tracking

```python
from app.core.sentry_config import SentryManager

# Manually capture exception
try:
    risky_operation()
except Exception as e:
    SentryManager.capture_exception(
        e,
        extra={"context": "batch_processing"}
    )

# Track user activity
SentryManager.add_breadcrumb(
    message="User started analysis",
    category="user_action"
)

# Set user context
SentryManager.set_user_context(
    user_id="123",
    email="user@example.com",
    role="admin"
)
```

---

## 📊 Log File Format

### Structured JSON Log (Production)

```json
{
  "timestamp": "2026-03-20T10:30:45.123Z",
  "environment": "production",
  "service": "ai-adaptive-onboarding-engine",
  "version": "3.0.0",
  "hostname": "api-server-01",
  "level": "INFO",
  "message": "POST /api/v1/analyze - 200",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/v1/analyze",
  "query": "",
  "status_code": 200,
  "duration_ms": 1234.56,
  "response_size_bytes": 2048,
  "client_ip": "192.168.1.100",
  "user_id": "123",
  "user_role": "user",
  "user_agent": "Mozilla/5.0...",
  "request_log": true
}
```

### Colored Console Log (Development)

```
[2026-03-20 10:30:45] - app - INFO - POST /api/v1/analyze - 200
[2026-03-20 10:30:46] - app.core.database - DEBUG - SELECT users FROM ... duration=5.23ms
[2026-03-20 10:30:47] - app - WARNING - High latency detected endpoint=/api/analyze duration_ms=5000
[2026-03-20 10:30:48] - app - ERROR - Unhandled exception in POST /api/analysis exception_type=ValueError
```

---

## 🚀 Performance Profiling

### Collecting Profile Data

```python
from app.core.performance import (
    performance_profiler,
    get_profiling_summary
)

# Data collected automatically via decorator
@profile_function("analyze_resume")
async def analyze_resume(file_content):
    # profiled automatically
    pass

# Get summary
summary = get_profiling_summary()
"""
{
  "analyze_resume": {
    "call_count": 150,
    "success_count": 148,
    "error_count": 2,
    "success_rate": 98.67,
    "total_duration_ms": 5432.10,
    "avg_duration_ms": 36.21,
    "min_duration_ms": 12.30,
    "max_duration_ms": 89.50,
    "p95_duration_ms": 75.40,
    "p99_duration_ms": 85.20
  }
}
"""

# Export to CSV for analysis
performance_profiler.export_csv("profiling_report.csv")
```

### Memory Profiling

```python
from app.core.performance import memory_profiler

# Take memory snapshot
memory_profiler.take_snapshot("before_operation")

# Perform operation
process_large_dataset()

# Take another snapshot
memory_profiler.take_snapshot("after_operation")

# View results
snapshots = memory_profiler.get_summary()
```

---

## 📋 Monitoring API Endpoints

### 1. Health Check (Public)

```bash
curl http://localhost:8000/api/v1/health

# Response
{
  "status": "healthy",
  "version": "3.0.0",
  "environment": "development",
  "service": "AI Adaptive Onboarding Engine"
}
```

### 2. Prometheus Metrics (Admin)

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/metrics/prometheus

# Returns metrics in Prometheus text format
```

### 3. Performance Summary (Admin)

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/metrics/performance

# Response
{
  "performance_profiling": {
    "analyze_resume": {
      "call_count": 150,
      "avg_duration_ms": 36.21,
      "p95_duration_ms": 75.40,
      ...
    }
  },
  "profiling_enabled": false
}
```

### 4. Metrics Status (Public)

```bash
curl http://localhost:8000/api/v1/metrics/status

# Response
{
  "prometheus_metrics": "enabled",
  "logging": "enabled",
  "sentry": "enabled" | "disabled",
  "profiling": "enabled",
  "status": "all_systems_operational"
}
```

---

## 🔒 Security Notes

### Sensitive Data Handling

1. **Password Fields** - Never logged, automatically redacted
2. **Authorization Headers** - Redacted from logs
3. **API Keys** - Redacted from logs
4. **Request/Response Bodies** - Disabled by default (enable carefully)

```python
# In logging middleware
safe_headers = self._get_safe_headers({
    "authorization": "Bearer token",  # Redacted
    "x-api-key": "sk-123",            # Redacted
    "user-agent": "Mozilla/5.0"       # Kept
})
```

### Production Security Checklist

```
□ Set ENVIRONMENT=production
□ Set DEBUG=False
□ Use json log format (not colored)
□ Set LOG_LEVEL=WARNING (reduce noise)
□ Enable SENTRY_DSN for error tracking
□ Set SENTRY_TRACES_SAMPLE_RATE=0.05-0.1
□ Disable LOG_REQUEST_BODY_ENABLED
□ Disable LOG_RESPONSE_BODY_ENABLED
□ Set LOG_MAX_BYTES appropriate for disk space
□ Set LOG_BACKUP_COUNT to reasonable value
□ Configure log rotation and cleanup
□ Set PROMETHEUS_PROFILES_SAMPLE_RATE < 0.1
□ Review Sentry PII settings
□ Monitor log file disk usage
□ Setup log aggregation (ELK, Splunk, etc.)
□ Setup Prometheus scraping from monitoring server
```

---

## 🔄 Integration Points

### With FastAPI Routes

```python
from fastapi import FastAPI, Depends
from app.core.logging_config import logger
from app.core.prometheus_config import PrometheusMetrics
from app.core.performance import profile_function

@app.post("/api/v1/analyze")
@profile_function("analyze_endpoint")
async def analyze(resume_text: str):
    # Logging automatically done by middleware
    logger.info(f"Analyzing resume for user {current_user.id}")
    
    result = await analyze_resume(resume_text)
    
    # Metrics automatically recorded
    PrometheusMetrics.record_analysis("resume", duration)
    
    return result
```

### With Database Operations

```python
from app.core.prometheus_config import PrometheusMetrics

def get_user(user_id: int):
    start = time.time()
    
    user = db.query(User).filter(User.id == user_id).first()
    
    duration = time.time() - start
    PrometheusMetrics.record_db_query(
        operation="SELECT",
        table="users",
        duration=duration
    )
    
    return user
```

### With Error Handling

```python
from app.core.sentry_config import SentryManager

@app.exception_handler(Exception)
async def error_handler(request, exc):
    # Logged by ErrorLoggingMiddleware
    # Captured in Sentry automatically
    
    return {"error": "Internal Server Error"}
```

---

## 📚 Log Files Location

```
logs/
├── app.log           # Main application log (JSON/colored)
│                     # Auto-rotated daily or at 100MB
├── app.log.1         # Backup 1
├── app.log.2         # Backup 2
├── app.log.3         # Backup 3
│   ...
└── error.log         # Errors only (always enabled)
    ├── error.log.1
    └── error.log.2
```

---

## 🎛️ Advanced Configuration

### Custom Log Filtering

```python
# In logging_config.py
class CustomFilter(logging.Filter):
    def filter(self, record):
        # Only log if certain conditions
        return "important" in record.getMessage()

logger.addFilter(CustomFilter())
```

### Custom Metrics

```python
# Add custom gauge metric
from app.core.prometheus_config import PrometheusMetrics

PrometheusMetrics.set_gauge_metric("cache_hit_rate", 95.5)
```

### Custom Prometheus Metrics

```python
# Add to PrometheusMetrics class
CUSTOM_METRIC = Gauge(
    "custom_metric_name",
    "Description",
    registry=PrometheusMetrics.REGISTRY
)

# Use it
CUSTOM_METRIC.set(value)
```

---

## 🧪 Testing Logging

```bash
# Test logging system
curl -H "Authorization: Bearer TOKEN" \
  -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!"}'

# Check logs
tail -f logs/app.log

# Test monitoring
curl http://localhost:8000/api/v1/metrics/status
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/metrics/performance
```

---

## 📖 Environment-Specific Setup

### Local Development

```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_FORMAT=colored
SENTRY_DSN=  # Empty
PROFILING_ENABLED=False
PROMETHEUS_ENABLED=True
```

### Staging

```bash
ENVIRONMENT=staging
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=https://key@sentry.io/staging
SENTRY_TRACES_SAMPLE_RATE=0.1
PROFILING_ENABLED=True
PROFILING_SAMPLE_RATE=0.05
```

### Production

```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
LOG_FORMAT=json
SENTRY_DSN=https://key@sentry.io/production
SENTRY_TRACES_SAMPLE_RATE=0.01
SENTRY_PROFILES_SAMPLE_RATE=0.01
PROFILING_ENABLED=False  # Disable unless needed
LOG_REQUEST_BODY_ENABLED=False
LOG_RESPONSE_BODY_ENABLED=False
```

---

## ⚠️ Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Disk space filling up | Large log files not rotated | Check LOG_MAX_BYTES setting |
| Missing Sentry events | DSN not configured | Set SENTRY_DSN in .env |
| Prometheus scraping fails | Metrics endpoint not accessible | Check port 8000 access |
| Slow performance | Profiling enabled | Set PROFILING_ENABLED=False |
| JSON logs not appearing | LOG_FORMAT set to colored | Set LOG_FORMAT=json |

---

## 🔮 Next Steps (Phase 4)

- [ ] Audit logging for user actions
- [ ] OAuth2/SSO integration
- [ ] Advanced access control (ACL)
- [ ] Data encryption at rest
- [ ] Compliance logging (GDPR, SOC2)
- [ ] Custom alerting rules
- [ ] Log aggregation service (ELK, Splunk)
- [ ] Real-time dashboards (Grafana)

---

## 📊 Metrics Glossary

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method/endpoint/status |
| `http_request_duration_seconds` | Histogram | Request latency in seconds |
| `http_response_size_bytes` | Summary | Response body size |
| `db_queries_total` | Counter | Database operations performed |
| `db_query_duration_seconds` | Histogram | Database query latency |
| `errors_total` | Counter | Application errors by type |
| `login_attempts_total` | Counter | Login success/failure counts |
| `analyses_total` | Counter | Analysis operations performed |
| `rate_limited_requests_total` | Counter | Requests blocked by rate limiter |
| `active_sessions` | Gauge | Current active user sessions |

---

## ✉️ Support & References

**Documentation**
- [Structured Logging Best Practices](https://cloud.google.com/logging/docs/structured-logging)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Python Logging Module](https://docs.python.org/3/library/logging.html)

**Configuration Templates**
- See `.env.example` for all configuration options
- See `app/core/config.py` for default values

**Monitoring Setup**
- Prometheus Alertmanager rules
- Grafana dashboard templates
- Sentry alert policies

---

**Status**: ✅ COMPLETE

**Phase**: 3 - Logging & Monitoring

**Date**: March 20, 2026

**Files Created**: 7 new modules

**Lines Added**: 1,780+ lines of production code

**Next Phase**: Phase 4 - Advanced Security Features

