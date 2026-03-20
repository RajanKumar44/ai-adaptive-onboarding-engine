"""
Prometheus Metrics Module

Provides application metrics collection:
- Request count by endpoint and method
- Request latency distribution
- Database query metrics
- Error rates by type
- Custom business metrics
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    CollectorRegistry, generate_latest
)
from typing import Dict, Optional
import time
import logging


logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Centralized Prometheus metrics manager"""
    
    # Create custom registry (don't use default to avoid conflicts)
    REGISTRY = CollectorRegistry()
    
    # Request metrics
    REQUEST_COUNT = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
        registry=REGISTRY
    )
    
    REQUEST_DURATION = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "endpoint"],
        buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        registry=REGISTRY
    )
    
    # Response size metrics
    RESPONSE_SIZE = Summary(
        "http_response_size_bytes",
        "HTTP response size in bytes",
        ["method", "endpoint"],
        registry=REGISTRY
    )
    
    # Database metrics
    DB_QUERIES = Counter(
        "db_queries_total",
        "Total database queries",
        ["operation", "table"],
        registry=REGISTRY
    )
    
    DB_QUERY_DURATION = Histogram(
        "db_query_duration_seconds",
        "Database query duration in seconds",
        ["operation", "table"],
        buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
        registry=REGISTRY
    )
    
    # Error metrics
    ERRORS_TOTAL = Counter(
        "errors_total",
        "Total errors",
        ["error_type", "endpoint"],
        registry=REGISTRY
    )
    
    # Authentication metrics
    LOGIN_ATTEMPTS = Counter(
        "login_attempts_total",
        "Total login attempts",
        ["result"],  # success, failure
        registry=REGISTRY
    )
    
    ACTIVE_SESSIONS = Gauge(
        "active_sessions",
        "Number of active user sessions",
        registry=REGISTRY
    )
    
    # Analysis metrics
    ANALYSES_TOTAL = Counter(
        "analyses_total",
        "Total analyses performed",
        ["skill_category"],
        registry=REGISTRY
    )
    
    ANALYSIS_DURATION = Histogram(
        "analysis_duration_seconds",
        "Analysis duration in seconds",
        ["skill_category"],
        buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
        registry=REGISTRY
    )
    
    # Rate limiting metrics
    RATE_LIMITED_REQUESTS = Counter(
        "rate_limited_requests_total",
        "Total rate limited requests",
        ["endpoint"],
        registry=REGISTRY
    )
    
    # Custom gauge metrics
    SYSTEM_METRICS = {
        "queue_length": Gauge(
            "queue_length",
            "Current queue length",
            registry=REGISTRY
        ),
        "cache_hit_rate": Gauge(
            "cache_hit_rate",
            "Cache hit rate (percentage)",
            registry=REGISTRY
        ),
    }
    
    @classmethod
    def record_request(cls, method: str, endpoint: str, status: int, 
                      duration: float, response_size: int = 0):
        """Record HTTP request metrics"""
        try:
            cls.REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()
            
            cls.REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            if response_size > 0:
                cls.RESPONSE_SIZE.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)
        except Exception as e:
            logger.error(f"Error recording request metrics: {str(e)}")
    
    @classmethod
    def record_db_query(cls, operation: str, table: str, duration: float):
        """Record database query metrics"""
        try:
            cls.DB_QUERIES.labels(
                operation=operation,
                table=table
            ).inc()
            
            cls.DB_QUERY_DURATION.labels(
                operation=operation,
                table=table
            ).observe(duration)
        except Exception as e:
            logger.error(f"Error recording DB metrics: {str(e)}")
    
    @classmethod
    def record_error(cls, error_type: str, endpoint: str):
        """Record error metrics"""
        try:
            cls.ERRORS_TOTAL.labels(
                error_type=error_type,
                endpoint=endpoint
            ).inc()
        except Exception as e:
            logger.error(f"Error recording error metrics: {str(e)}")
    
    @classmethod
    def record_login_attempt(cls, success: bool):
        """Record login attempt metrics"""
        try:
            result = "success" if success else "failure"
            cls.LOGIN_ATTEMPTS.labels(result=result).inc()
        except Exception as e:
            logger.error(f"Error recording login metrics: {str(e)}")
    
    @classmethod
    def set_active_sessions(cls, count: int):
        """Set active sessions gauge"""
        try:
            cls.ACTIVE_SESSIONS.set(count)
        except Exception as e:
            logger.error(f"Error setting active sessions: {str(e)}")
    
    @classmethod
    def record_analysis(cls, skill_category: str, duration: float):
        """Record analysis metrics"""
        try:
            cls.ANALYSES_TOTAL.labels(skill_category=skill_category).inc()
            
            cls.ANALYSIS_DURATION.labels(
                skill_category=skill_category
            ).observe(duration)
        except Exception as e:
            logger.error(f"Error recording analysis metrics: {str(e)}")
    
    @classmethod
    def record_rate_limited(cls, endpoint: str):
        """Record rate limited request"""
        try:
            cls.RATE_LIMITED_REQUESTS.labels(endpoint=endpoint).inc()
        except Exception as e:
            logger.error(f"Error recording rate limit metrics: {str(e)}")
    
    @classmethod
    def set_gauge_metric(cls, metric_name: str, value: float):
        """Set a gauge metric value"""
        try:
            if metric_name in cls.SYSTEM_METRICS:
                cls.SYSTEM_METRICS[metric_name].set(value)
        except Exception as e:
            logger.error(f"Error setting gauge metric {metric_name}: {str(e)}")
    
    @classmethod
    def get_metrics_text(cls) -> str:
        """Get all metrics in Prometheus text format"""
        try:
            return generate_latest(cls.REGISTRY).decode("utf-8")
        except Exception as e:
            logger.error(f"Error generating metrics: {str(e)}")
            return ""
    
    @classmethod
    def get_metric_summary(cls) -> dict:
        """Get a summary of all metrics"""
        summary = {
            "requests_total": {},
            "errors_total": {},
            "analyses_total": {},
            "login_attempts": {}
        }
        
        # Collect counter values (simplified - actual implementation
        # would parse the metrics registry)
        try:
            for collector in cls.REGISTRY._collector_to_names:
                if "requests_total" in str(collector):
                    summary["requests_total"] = str(collector)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
        
        return summary


class MetricsContext:
    """Context manager for timing operations"""
    
    def __init__(self, metric: Histogram, labels: Dict[str, str]):
        self.metric = metric
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metric.labels(**self.labels).observe(duration)
        return False


def init_prometheus():
    """Initialize Prometheus metrics"""
    logger.info("Prometheus metrics initialized")
    return PrometheusMetrics.REGISTRY
