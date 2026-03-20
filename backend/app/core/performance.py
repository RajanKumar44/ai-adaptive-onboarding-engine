"""
Performance Profiling Module

Provides tools for profiling and performance analysis:
- Function timing and profiling
- Memory usage tracking
- Bottleneck identification
- Performance reports
"""

import time
import functools
import logging
from typing import Callable, Optional, Dict, List
from collections import defaultdict
from datetime import datetime
import asyncio
import tracemalloc


logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Main profiler for tracking function performance"""
    
    def __init__(self):
        self.records: Dict[str, List[Dict]] = defaultdict(list)
        self.enabled = True
    
    def record(self, function_name: str, duration: float, success: bool, 
              error: Optional[str] = None):
        """Record a function call"""
        if not self.enabled:
            return
        
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": round(duration * 1000, 2),
            "success": success,
            "error": error
        }
        
        self.records[function_name].append(record)
        
        # Keep only last 100 records per function
        if len(self.records[function_name]) > 100:
            self.records[function_name] = self.records[function_name][-100:]
    
    def get_summary(self, function_name: Optional[str] = None) -> Dict:
        """Get summary statistics for profiled functions"""
        
        summary = {}
        
        functions = [function_name] if function_name else self.records.keys()
        
        for func_name in functions:
            if func_name not in self.records or not self.records[func_name]:
                continue
            
            records = self.records[func_name]
            durations = [r["duration_ms"] for r in records if r["success"]]
            
            if not durations:
                continue
            
            error_count = sum(1 for r in records if not r["success"])
            success_rate = ((len(records) - error_count) / len(records)) * 100
            
            summary[func_name] = {
                "call_count": len(records),
                "success_count": len(records) - error_count,
                "error_count": error_count,
                "success_rate": round(success_rate, 2),
                "total_duration_ms": round(sum(durations), 2),
                "avg_duration_ms": round(sum(durations) / len(durations), 2),
                "min_duration_ms": round(min(durations), 2),
                "max_duration_ms": round(max(durations), 2),
                "p95_duration_ms": round(sorted(durations)[int(len(durations) * 0.95)], 2) if durations else 0,
                "p99_duration_ms": round(sorted(durations)[int(len(durations) * 0.99)], 2) if durations else 0
            }
        
        return summary
    
    def clear(self):
        """Clear all records"""
        self.records.clear()
    
    def export_csv(self, filename: str):
        """Export profiling data to CSV"""
        import csv
        
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "function", "timestamp", "duration_ms", "success", "error"
                ])
                
                for func_name, records in self.records.items():
                    for record in records:
                        writer.writerow([
                            func_name,
                            record["timestamp"],
                            record["duration_ms"],
                            record["success"],
                            record["error"] or ""
                        ])
        except Exception as e:
            logger.error(f"Error exporting profiling data: {str(e)}")


class MemoryProfiler:
    """Memory usage profiler"""
    
    def __init__(self):
        self.snapshots = []
        self.enabled = True
    
    def take_snapshot(self, label: str = ""):
        """Take a memory snapshot"""
        if not self.enabled:
            return
        
        try:
            tracemalloc.start()
            snapshot = tracemalloc.take_snapshot()
            
            # Get top memory consumers
            top_stats = snapshot.statistics("lineno")[:10]
            
            self.snapshots.append({
                "timestamp": datetime.utcnow().isoformat(),
                "label": label,
                "top_allocations": [
                    {
                        "file": str(stat.traceback[0].filename),
                        "line": stat.traceback[0].lineno,
                        "size_mb": round(stat.size / 1024 / 1024, 2)
                    }
                    for stat in top_stats
                ]
            })
        except Exception as e:
            logger.error(f"Error taking memory snapshot: {str(e)}")
    
    def get_summary(self) -> List[Dict]:
        """Get memory profile summary"""
        return self.snapshots
    
    def clear(self):
        """Clear snapshots"""
        self.snapshots.clear()


class RequestProfiler:
    """Track request profiling data"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def record_request(self, endpoint: str, duration: float, memory_used: float):
        """Record request performance"""
        self.requests[endpoint].append({
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": round(duration * 1000, 2),
            "memory_mb": round(memory_used, 2)
        })
        
        # Keep only last 100 requests per endpoint
        if len(self.requests[endpoint]) > 100:
            self.requests[endpoint] = self.requests[endpoint][-100:]
    
    def get_endpoint_stats(self, endpoint: str) -> Dict:
        """Get stats for an endpoint"""
        if endpoint not in self.requests or not self.requests[endpoint]:
            return {}
        
        records = self.requests[endpoint]
        durations = [r["duration_ms"] for r in records]
        memory_usage = [r["memory_mb"] for r in records]
        
        return {
            "request_count": len(records),
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "min_duration_ms": round(min(durations), 2),
            "max_duration_ms": round(max(durations), 2),
            "avg_memory_mb": round(sum(memory_usage) / len(memory_usage), 2),
            "max_memory_mb": round(max(memory_usage), 2)
        }


# Global profiler instances
performance_profiler = PerformanceProfiler()
memory_profiler = MemoryProfiler()
request_profiler = RequestProfiler()


def profile_function(func_name: Optional[str] = None):
    """Decorator for profiling function performance"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = func_name or func.__qualname__
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                performance_profiler.record(name, duration, True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_profiler.record(
                    name, duration, False, str(e)
                )
                logger.error(f"Error in {name}: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = func_name or func.__qualname__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                performance_profiler.record(name, duration, True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_profiler.record(
                    name, duration, False, str(e)
                )
                logger.error(f"Error in {name}: {str(e)}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def get_profiling_summary() -> Dict:
    """Get complete profiling summary"""
    return {
        "performance": performance_profiler.get_summary(),
        "memory": memory_profiler.get_summary(),
        "enabled": performance_profiler.enabled
    }


def reset_profiling():
    """Reset all profiling data"""
    performance_profiler.clear()
    memory_profiler.clear()
