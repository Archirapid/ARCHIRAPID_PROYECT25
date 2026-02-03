#!/usr/bin/env python3
"""
Performance optimization utilities for ARCHIRAPID
Caching, lazy loading, and optimization helpers
"""

import time
import functools
from typing import Any, Callable, Dict, Optional
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
import json


class LRUCache:
    """
    Least Recently Used (LRU) cache implementation with TTL support
    
    Note: This implementation is NOT thread-safe. For multi-threaded environments,
    consider using threading.Lock or a thread-safe alternative like cachetools.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Initialize LRU cache
        
        Args:
            max_size: Maximum number of items in cache
            ttl_seconds: Time to live for cached items in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = OrderedDict()
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None
        
        # Check if expired
        if self._is_expired(key):
            self._cache.pop(key)
            self._timestamps.pop(key)
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return self._cache[key]
    
    def set(self, key: str, value: Any):
        """
        Set item in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest item if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = next(iter(self._cache))
            self._cache.pop(oldest_key)
            self._timestamps.pop(oldest_key)
        
        # Add/update item
        self._cache[key] = value
        self._cache.move_to_end(key)
        self._timestamps[key] = datetime.now()
    
    def clear(self):
        """Clear all cached items"""
        self._cache.clear()
        self._timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cached item is expired"""
        if key not in self._timestamps:
            return True
        
        timestamp = self._timestamps[key]
        age = (datetime.now() - timestamp).total_seconds()
        return age > self.ttl_seconds


# Global cache instance
_global_cache = LRUCache()


def get_cache() -> LRUCache:
    """Get global cache instance"""
    return _global_cache


def cache_result(ttl_seconds: int = 300, key_func: Callable = None):
    """
    Decorator to cache function results
    
    Args:
        ttl_seconds: Time to live for cached result
        key_func: Optional function to generate cache key from arguments
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: hash of function name and arguments
                key_data = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                cache_key = hashlib.md5(
                    json.dumps(key_data, sort_keys=True, default=str).encode()
                ).hexdigest()
            
            # Try to get from cache
            cache = get_cache()
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator


class Timer:
    """
    Context manager for timing code execution
    Useful for identifying performance bottlenecks
    """
    
    def __init__(self, name: str = "Operation", log_func: Callable = None):
        """
        Initialize timer
        
        Args:
            name: Name of the operation being timed
            log_func: Optional logging function (default: print)
        """
        self.name = name
        self.log_func = log_func or print
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.log_func(f"{self.name} took {duration:.3f} seconds")
    
    @property
    def duration(self) -> float:
        """Get duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


def debounce(wait_seconds: float):
    """
    Decorator to debounce function calls
    Useful for preventing excessive API calls from UI interactions
    
    Args:
        wait_seconds: Minimum time between function calls
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        last_call_time = [0]  # Use list to allow mutation in closure
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            time_since_last_call = current_time - last_call_time[0]
            
            if time_since_last_call >= wait_seconds:
                last_call_time[0] = current_time
                return func(*args, **kwargs)
            
            return None  # Debounced - don't execute
        
        return wrapper
    return decorator


def lazy_load(loader_func: Callable, cache_key: str = None):
    """
    Lazy loading decorator
    Loads data only when first accessed
    
    Args:
        loader_func: Function to load data
        cache_key: Optional cache key
    
    Returns:
        Decorator
    """
    def decorator(func: Callable) -> Callable:
        loaded_data = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = cache_key or func.__name__
            
            if key not in loaded_data:
                loaded_data[key] = loader_func(*args, **kwargs)
            
            return loaded_data[key]
        
        return wrapper
    return decorator


def batch_process(items: list, batch_size: int = 10, process_func: Callable = None):
    """
    Process items in batches to improve performance
    
    Args:
        items: List of items to process
        batch_size: Number of items per batch
        process_func: Function to process each batch
    
    Returns:
        List of results
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        if process_func:
            batch_result = process_func(batch)
            results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
        else:
            results.extend(batch)
    
    return results


class PerformanceMonitor:
    """
    Monitor and track performance metrics
    """
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name: str, value: float, unit: str = "ms"):
        """
        Record a performance metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
        """
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'unit': unit,
            'timestamp': datetime.now()
        })
    
    def get_average(self, name: str) -> Optional[float]:
        """Get average value for a metric"""
        if name not in self.metrics or not self.metrics[name]:
            return None
        
        values = [m['value'] for m in self.metrics[name]]
        return sum(values) / len(values)
    
    def get_summary(self) -> Dict:
        """Get summary of all metrics"""
        summary = {}
        
        for name, measurements in self.metrics.items():
            if measurements:
                values = [m['value'] for m in measurements]
                summary[name] = {
                    'count': len(values),
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'unit': measurements[0]['unit']
                }
        
        return summary


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _performance_monitor
