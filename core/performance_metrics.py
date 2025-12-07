# -*- coding: utf-8 -*-
"""
Performance metrics module for SecInterp plugin.

This module provides tools for tracking performance and resource usage
across the plugin's operations.
"""

import time
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from ..logger_config import get_logger

logger = get_logger(__name__)

class MetricsCollector:
    """Collects and aggregates performance metrics."""
    
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.counts: Dict[str, int] = {}
        self.metadata: Dict[str, Any] = {}
        self._start_time = time.perf_counter()
        
    def record_timing(self, operation: str, duration: float) -> None:
        """Record duration of an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
        """
        self.timings[operation] = duration
        
    def record_count(self, metric: str, count: int) -> None:
        """Record a count metric (e.g. number of points).
        
        Args:
            metric: Name of the metric
            count: Count value
        """
        self.counts[metric] = count
        
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the metrics collection.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics.
        
        Returns:
            Dictionary with all collected metrics
        """
        return {
            'timings': self.timings,
            'counts': self.counts,
            'metadata': self.metadata,
            'total_duration': time.perf_counter() - self._start_time
        }
    
    def clear(self) -> None:
        """Clear all collected metrics."""
        self.timings.clear()
        self.counts.clear()
        self.metadata.clear()
        self._start_time = time.perf_counter()

class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(
        self, 
        operation_name: str, 
        collector: Optional[MetricsCollector] = None,
        logger_func: Optional[callable] = None
    ):
        """Initialize timer.
        
        Args:
            operation_name: Name of operation to measure
            collector: Optional metrics collector to record into
            logger_func: Optional logger function for immediate logging
        """
        self.operation_name = operation_name
        self.collector = collector
        self.logger_func = logger_func
        self.start_time: float = 0.0
        self.duration: float = 0.0
        
    def __enter__(self):
        """Start the timer.
        
        Returns:
            self: The timer instance
        """
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the timer and record/log validity.
        
        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        self.duration = time.perf_counter() - self.start_time
        
        if self.collector:
            self.collector.record_timing(self.operation_name, self.duration)
            
        if self.logger_func:
            self.logger_func(f"{self.operation_name}: {self.duration:.3f}s")


def format_duration(seconds: float) -> str:
    """Format duration in human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g. "1.2s", "150ms")
    """
    if seconds < 0.001:
        return f"{seconds*1000000:.0f}µs"
    
    if seconds < 1.0:
        return f"{seconds*1000:.0f}ms"
        
    return f"{seconds:.1f}s"
