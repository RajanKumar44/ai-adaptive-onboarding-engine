"""
Structured Logging Configuration Module

Provides centralized logging setup with:
- JSON structured logging for production
- Colored console logging for development
- File rotation and archival
- Multiple log levels for different components
- Performance timing utilities
"""

import logging
import logging.handlers
import json
import time
import os
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import colorlog
from pythonjsonlogger import jsonlogger
from functools import wraps
from .config import settings


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, 
                   message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record["timestamp"] = datetime.utcnow().isoformat()
        
        # Add environment
        log_record["environment"] = settings.ENVIRONMENT
        
        # Add service version
        log_record["service"] = "ai-adaptive-onboarding-engine"
        log_record["version"] = "3.0.0"
        
        # Add hostname
        log_record["hostname"] = os.environ.get("HOSTNAME", "unknown")
        
        # Ensure message is always present
        if "message" not in log_record:
            log_record["message"] = record.getMessage()


class LoggerManager:
    """Centralized logger manager for application"""
    
    _loggers: Dict[str, logging.Logger] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls, log_dir: str = "logs") -> None:
        """Initialize logging system"""
        if cls._initialized:
            return
        
        # Create logs directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(settings.LOG_LEVEL)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler with colors (development)
        if settings.LOG_FORMAT == "colored":
            console_handler = logging.StreamHandler()
            console_handler.setLevel(settings.LOG_LEVEL)
            
            # Colored format
            formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s[%(asctime)s]%(reset)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler with JSON format (production)
        if settings.LOG_FORMAT == "json" or settings.ENVIRONMENT == "production":
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_path / "app.log",
                maxBytes=settings.LOG_MAX_BYTES,  # 100 MB
                backupCount=settings.LOG_BACKUP_COUNT  # Keep 10 backups
            )
            file_handler.setLevel(settings.LOG_LEVEL)
            json_formatter = StructuredFormatter()
            file_handler.setFormatter(json_formatter)
            root_logger.addHandler(file_handler)
        
        # Error log file handler (always enabled for production issues)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=log_path / "error.log",
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT
        )
        error_handler.setLevel(logging.ERROR)
        json_formatter = StructuredFormatter()
        error_handler.setFormatter(json_formatter)
        root_logger.addHandler(error_handler)
        
        # Suppress verbose loggers
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("alembic").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance"""
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        return cls._loggers[name]


# Global logger instance
logger = logging.getLogger("app")


class PerformanceTimer:
    """Context manager and decorator for performance timing"""
    
    def __init__(self, name: str, log_level: int = logging.DEBUG):
        self.name = name
        self.log_level = log_level
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0
    
    def __enter__(self):
        """Enter context manager"""
        self.start_time = time.time()
        logger.log(self.log_level, f"Started: {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        self.elapsed_time = time.time() - self.start_time
        
        if exc_type is None:
            logger.log(
                self.log_level,
                f"Completed: {self.name}",
                extra={
                    "duration_ms": round(self.elapsed_time * 1000, 2),
                    "performance_metric": True
                }
            )
        else:
            logger.error(
                f"Failed: {self.name}",
                extra={
                    "duration_ms": round(self.elapsed_time * 1000, 2),
                    "error": str(exc_val),
                    "performance_metric": True
                }
            )
        
        return False
    
    def get_elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        return self.elapsed_time * 1000


def log_performance(name: Optional[str] = None, log_level: int = logging.DEBUG):
    """Decorator for performance logging"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = name or func.__name__
            with PerformanceTimer(func_name, log_level):
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = name or func.__name__
            with PerformanceTimer(func_name, log_level):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def log_function_call(log_level: int = logging.DEBUG):
    """Decorator to log function calls with parameters"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.log(
                log_level,
                f"Calling {func.__name__}",
                extra={"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
            )
            try:
                result = await func(*args, **kwargs)
                logger.log(log_level, f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}",
                    extra={"exception_type": type(e).__name__},
                    exc_info=True
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.log(
                log_level,
                f"Calling {func.__name__}",
                extra={"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
            )
            try:
                result = func(*args, **kwargs)
                logger.log(log_level, f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}",
                    extra={"exception_type": type(e).__name__},
                    exc_info=True
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Initialize logging
LoggerManager.initialize("logs")


import asyncio
