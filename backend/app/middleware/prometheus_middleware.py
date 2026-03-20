"""
Prometheus Metrics Middleware

Integrates Prometheus metrics collection with FastAPI:
- Automatic request metrics
- Endpoint tracking
- Performance monitoring
- Error tracking
"""

import time
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.prometheus_config import PrometheusMetrics


logger = logging.getLogger(__name__)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics"""
    
    def __init__(self, app, skip_paths=None):
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/health",
            "/api/v1/health",
            "/metrics",
            "/api/v1/metrics",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercept request and collect metrics"""
        
        # Skip metrics collection for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        # Normalize endpoint path (remove IDs for better grouping)
        endpoint = self._normalize_endpoint(path)
        
        response_status = 500
        response_size = 0
        
        try:
            # Call the endpoint
            response = await call_next(request)
            response_status = response.status_code
            
            # Get response size
            try:
                response_size = int(response.headers.get("content-length", 0))
            except:
                response_size = 0
            
        except Exception as e:
            # Record error metrics
            PrometheusMetrics.record_error(
                error_type=type(e).__name__,
                endpoint=endpoint
            )
            logger.error(f"Error in request {method} {path}: {str(e)}")
            raise
        
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            try:
                PrometheusMetrics.record_request(
                    method=method,
                    endpoint=endpoint,
                    status=response_status,
                    duration=duration,
                    response_size=response_size
                )
            except Exception as e:
                logger.error(f"Error recording metrics: {str(e)}")
        
        return response
    
    @staticmethod
    def _normalize_endpoint(path: str) -> str:
        """Normalize endpoint path for better metric grouping"""
        
        # Remove UUID/ID from paths like /users/{id}
        parts = path.split("/")
        normalized = []
        
        for part in parts:
            # Check if part looks like a UUID or ID
            if part and (
                len(part) == 36 and part.count("-") == 4 or  # UUID
                part.isdigit() or  # Integer ID
                part.startswith("{") and part.endswith("}")  # Path parameter
            ):
                normalized.append("{id}")
            else:
                normalized.append(part)
        
        return "/".join(normalized)


class MetricsRecorderMiddleware(BaseHTTPMiddleware):
    """Additional middleware for recording specific metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Record additional application metrics"""
        
        response = await call_next(request)
        
        # Record login attempts
        if request.url.path == "/api/v1/auth/login":
            success = response.status_code == 200
            PrometheusMetrics.record_login_attempt(success)
        
        # Record analyses
        if request.url.path == "/api/v1/analyze" and request.method == "POST":
            # These will be recorded in the analyze endpoint itself
            pass
        
        # Record rate limit hits
        if response.status_code == 429:
            endpoint = request.url.path
            PrometheusMetrics.record_rate_limited(endpoint)
        
        return response


class DatabaseMetricsMiddleware:
    """Middleware for database query metrics (used with SQLAlchemy events)"""
    
    @staticmethod
    def setup_db_metrics(engine):
        """Setup database metrics collection with SQLAlchemy"""
        
        from sqlalchemy import event
        
        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record database query start time"""
            conn.info.setdefault('query_start_time', []).append(time.time())
        
        @event.listens_for(engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Record database query metrics"""
            try:
                total = time.time() - conn.info['query_start_time'].pop(-1)
                
                # Extract operation and table from SQL
                operation = "query"
                table = "unknown"
                
                statement_upper = statement.strip().upper()
                
                if statement_upper.startswith("SELECT"):
                    operation = "SELECT"
                elif statement_upper.startswith("INSERT"):
                    operation = "INSERT"
                elif statement_upper.startswith("UPDATE"):
                    operation = "UPDATE"
                elif statement_upper.startswith("DELETE"):
                    operation = "DELETE"
                
                # Try to extract table name (simplified)
                words = statement.split()
                for i, word in enumerate(words):
                    if word.upper() in ("FROM", "INTO", "UPDATE"):
                        if i + 1 < len(words):
                            table = words[i + 1].replace(";", "").replace(",", "")
                            break
                
                # Record metrics
                PrometheusMetrics.record_db_query(operation, table, total)
                
            except Exception as e:
                logger.error(f"Error recording DB metrics: {str(e)}")
