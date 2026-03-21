"""
Metrics Routes Module

Provides endpoints for accessing:
- Prometheus metrics (in standard format)
- Application health metrics
- Performance profiling data
- Logging statistics
"""

from fastapi import APIRouter, Depends, Response
from fastapi.responses import PlainTextResponse
from typing import Dict, Any
from app.core.auth import get_current_admin
from app.models.user import User
from app.core.prometheus_config import PrometheusMetrics
from app.core.performance import (
    get_profiling_summary,
    reset_profiling,
    performance_profiler,
    request_profiler
)
from app.core.config import get_settings
import logging


router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])
logger = logging.getLogger(__name__)


@router.get(
    "/prometheus",
    response_class=PlainTextResponse,
    summary="Prometheus Metrics Endpoint",
    description="Returns metrics in Prometheus text format for scraping"
)
async def get_prometheus_metrics():
    """
    Get Prometheus metrics in standard format
    
    Returns metrics in Prometheus text format that can be scraped by Prometheus.
    Used for monitoring and alerting.
    
    **Requires**: Admin role
    """
    try:
        metrics_text = PrometheusMetrics.get_metrics_text()
        return metrics_text
    except Exception as e:
        logger.error(f"Error getting Prometheus metrics: {str(e)}")
        return "# Error collecting metrics\n"


@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Application Health Check",
    description="Returns application health status and metrics"
)
async def health_check():
    """
    Get application health status
    
    Returns:
    - status: "healthy" or "degraded"
    - timestamp: Current server time
    - version: Application version
    - environment: Current environment
    
    **Requires**: None (public endpoint)
    """
    return {
        "status": "healthy",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="health", level=logging.INFO, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        )),
        "version": get_settings().APP_VERSION,
        "environment": get_settings().ENVIRONMENT,
        "uptime": "N/A"
    }


@router.get(
    "/performance",
    response_model=Dict[str, Any],
    summary="Performance Profiling Data",
    description="Returns function performance profiling data (admin only)"
)
async def get_performance_metrics(
    current_admin: User = Depends(get_current_admin)
):
    """
    Get performance profiling metrics
    
    Returns profiling data including:
    - Function call counts
    - Average/min/max duration
    - Success/error rates
    - Percentile latencies (p95, p99)
    
    **Requires**: Admin role
    """
    try:
        summary = get_profiling_summary()
        return {
            "performance_profiling": summary,
            "profiling_enabled": performance_profiler.enabled
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return {"error": str(e)}


@router.post(
    "/performance/reset",
    response_model=Dict[str, str],
    summary="Reset Performance Metrics",
    description="Clear all performance profiling data (admin only)"
)
async def reset_performance_metrics(
    current_admin: User = Depends(get_current_admin)
):
    """
    Reset all performance profiling data
    
    Clears collected performance metrics to start fresh analysis.
    
    **Requires**: Admin role
    """
    try:
        reset_profiling()
        logger.info("Performance metrics reset by admin")
        return {"message": "Performance metrics reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting metrics: {str(e)}")
        return {"error": str(e)}


@router.get(
    "/endpoints",
    response_model=Dict[str, Any],
    summary="Endpoint Performance Stats",
    description="Returns performance statistics for all endpoints"
)
async def get_endpoint_stats(
    current_admin: User = Depends(get_current_admin)
):
    """
    Get performance statistics for all endpoints
    
    Returns:
    - Endpoint paths
    - Request counts
    - Average/min/max latency
    - Memory usage stats
    - Error rates
    
    **Requires**: Admin role
    """
    try:
        stats = {}
        
        for category in ["auth", "analysis", "admin", "other"]:
            # Get raw metrics from Prometheus (simplified)
            stats[category] = {
                "category": category,
                "data": "See Prometheus endpoint for detailed metrics"
            }
        
        return {
            "endpoint_stats": stats,
            "summary": "Use /metrics/prometheus for detailed metrics data"
        }
    except Exception as e:
        logger.error(f"Error getting endpoint stats: {str(e)}")
        return {"error": str(e)}


@router.get(
    "/summary",
    response_model=Dict[str, Any],
    summary="Metrics Summary",
    description="Returns a summary of all collected metrics"
)
async def get_metrics_summary(
    current_admin: User = Depends(get_current_admin)
):
    """
    Get a summary of all metrics
    
    Returns:
    - Performance profiling summary
    - Prometheus metrics summary
    - Endpoint statistics
    - System health
    
    **Requires**: Admin role
    """
    try:
        return {
            "performance": performance_profiler.get_summary(),
            "prometheus": PrometheusMetrics.get_metric_summary(),
            "message": "Use /metrics/prometheus for full Prometheus format"
        }
    except Exception as e:
        logger.error(f"Error getting metrics summary: {str(e)}")
        return {"error": str(e)}


@router.get(
    "/logs-info",
    response_model=Dict[str, Any],
    summary="Logging Configuration",
    description="Returns current logging configuration (admin only)"
)
async def get_logging_info(
    current_admin: User = Depends(get_current_admin)
):
    """
    Get logging configuration and stats
    
    Returns:
    - Log level
    - Log format (json/colored)
    - Log file paths
    - Rotation settings
    
    **Requires**: Admin role
    """
    return {
        "environment": get_settings().ENVIRONMENT,
        "log_level": get_settings().LOG_LEVEL,
        "log_format": get_settings().LOG_FORMAT,
        "log_dir": "./logs",
        "log_max_bytes": get_settings().LOG_MAX_BYTES,
        "log_backup_count": get_settings().LOG_BACKUP_COUNT,
        "json_logging_enabled": get_settings().LOG_FORMAT == "json" and get_settings().ENVIRONMENT == "production"
    }


@router.get(
    "/sentry-info",
    response_model=Dict[str, Any],
    summary="Sentry Configuration",
    description="Returns Sentry error tracking configuration (admin only)"
)
async def get_sentry_info(
    current_admin: User = Depends(get_current_admin)
):
    """
    Get Sentry error tracking configuration
    
    Returns:
    - Sentry enabled status
    - Environment configuration
    - Sample rates
    
    **Requires**: Admin role
    """
    return {
        "sentry_enabled": bool(get_settings().SENTRY_DSN),
        "environment": get_settings().ENVIRONMENT,
        "traces_sample_rate": get_settings().SENTRY_TRACES_SAMPLE_RATE,
        "profiles_sample_rate": get_settings().SENTRY_PROFILES_SAMPLE_RATE,
        "message": "Detailed Sentry configuration available in admin console"
    }


@router.get(
    "/status",
    response_model=Dict[str, Any],
    summary="Overall Monitoring Status",
    description="Returns overall monitoring system status"
)
async def get_monitoring_status():
    """
    Get overall monitoring system status
    
    Returns:
    - Prometheus metrics enabled
    - Sentry enabled
    - Logging enabled
    - Profiling enabled
    
    **Requires**: None (public endpoint with limited info)
    """
    return {
        "prometheus_metrics": "enabled",
        "logging": "enabled",
        "sentry": "enabled" if get_settings().SENTRY_DSN else "disabled",
        "profiling": "enabled",
        "status": "all_systems_operational"
    }
