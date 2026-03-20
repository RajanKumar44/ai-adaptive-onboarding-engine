"""
Request/Response Logging Middleware

Logs all HTTP requests and responses with:
- Request method, path, headers
- Response status code and time
- Payload details (request/response body size)
- User identification
- Error tracking
"""

import time
import json
import logging
from typing import Callable
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send


logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID for tracing"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to all requests"""
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Structured logging middleware for request/response tracking"""
    
    def __init__(self, app: ASGIApp, skip_paths: list = None):
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
        """Log request and response with performance metrics"""
        
        # Skip logging for health checks and metrics endpoints
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Generate request ID if not present
        request_id = getattr(request.state, "request_id", str(uuid4()))
        
        # Capture request details
        start_time = time.time()
        request_method = request.method
        request_path = request.url.path
        request_query = request.url.query or ""
        
        # Extract user info if authenticated
        user_id = None
        user_role = None
        try:
            if hasattr(request.state, "user"):
                user_id = request.state.user.id
                user_role = request.state.user.role
        except:
            pass
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Capture request headers (without sensitive data)
        safe_headers = self._get_safe_headers(dict(request.headers))
        
        response_status = 500
        response_size = 0
        
        try:
            # Call the actual endpoint
            response = await call_next(request)
            response_status = response.status_code
            
        except Exception as e:
            # Log exception
            logger.error(
                f"Request failed: {request_method} {request_path}",
                extra={
                    "request_id": request_id,
                    "method": request_method,
                    "path": request_path,
                    "query": request_query,
                    "client_ip": client_ip,
                    "user_id": user_id,
                    "user_role": user_role,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "headers": safe_headers,
                }
            )
            raise
        
        # Calculate response time
        duration = time.time() - start_time
        duration_ms = duration * 1000
        
        # Get response size from headers if available
        try:
            response_size = int(response.headers.get("content-length", 0))
        except:
            response_size = 0
        
        # Determine log level based on status code
        if response_status >= 500:
            log_level = logging.ERROR
        elif response_status >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        # Log structured request/response
        logger.log(
            log_level,
            f"{request_method} {request_path} - {response_status}",
            extra={
                "request_id": request_id,
                "method": request_method,
                "path": request_path,
                "query": request_query,
                "status_code": response_status,
                "duration_ms": round(duration_ms, 2),
                "response_size_bytes": response_size,
                "client_ip": client_ip,
                "user_id": user_id,
                "user_role": user_role,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "headers": safe_headers,
                "request_log": True
            }
        )
        
        # Add logging metadata to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(round(duration_ms, 2))
        
        return response
    
    @staticmethod
    def _get_safe_headers(headers: dict) -> dict:
        """Remove sensitive headers from logging"""
        sensitive_keys = {
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
            "password",
            "secret"
        }
        
        safe_headers = {}
        for key, value in headers.items():
            if key.lower() not in sensitive_keys:
                safe_headers[key] = value
            else:
                safe_headers[key] = "[REDACTED]"
        
        return safe_headers


class PerformanceMetricsMiddleware(BaseHTTPMiddleware):
    """Track performance metrics for different endpoint categories"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.metrics = {
            "auth": [],
            "analysis": [],
            "admin": [],
            "other": []
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track endpoint performance"""
        
        start_time = time.time()
        path = request.url.path
        
        # Categorize endpoint
        category = self._categorize_endpoint(path)
        
        response = await call_next(request)
        
        duration = (time.time() - start_time) * 1000
        
        # Store metric
        metric = {
            "path": path,
            "method": request.method,
            "status": response.status_code,
            "duration_ms": round(duration, 2),
            "timestamp": time.time()
        }
        
        self.metrics[category].append(metric)
        
        # Keep only last 1000 metrics per category
        if len(self.metrics[category]) > 1000:
            self.metrics[category] = self.metrics[category][-1000:]
        
        return response
    
    @staticmethod
    def _categorize_endpoint(path: str) -> str:
        """Categorize endpoint by path"""
        if "/auth/" in path:
            return "auth"
        elif "/analyze" in path or "/analysis" in path:
            return "analysis"
        elif "/admin/" in path:
            return "admin"
        else:
            return "other"
    
    def get_metrics_summary(self) -> dict:
        """Get summary of performance metrics"""
        summary = {}
        
        for category, metrics in self.metrics.items():
            if not metrics:
                continue
            
            durations = [m["duration_ms"] for m in metrics]
            summary[category] = {
                "total_requests": len(metrics),
                "avg_duration_ms": round(sum(durations) / len(durations), 2),
                "min_duration_ms": round(min(durations), 2),
                "max_duration_ms": round(max(durations), 2),
                "p95_duration_ms": round(sorted(durations)[int(len(durations) * 0.95)], 2) if durations else 0,
                "p99_duration_ms": round(sorted(durations)[int(len(durations) * 0.99)], 2) if durations else 0,
                "error_count": sum(1 for m in metrics if m["status"] >= 400)
            }
        
        return summary


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Special handling for errors with detailed logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Catch and log all errors with context"""
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            request_id = getattr(request.state, "request_id", str(uuid4()))
            
            # Log detailed error information
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "error": True
                },
                exc_info=True
            )
            
            # Re-raise to let error handlers process
            raise
