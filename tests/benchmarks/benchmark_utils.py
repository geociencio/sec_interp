"""Utilities for performance benchmarking in tests."""

import functools
import time
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def benchmark(func: Callable) -> Callable:
    """Decorator to measure and log execution time of a test method.

    Args:
        func: The test method to benchmark.

    Returns:
        The wrapped method.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.info(f"BENCHMARK: {func.__name__} took {duration:.4f} seconds")
            print(f"\n[BENCHMARK] {func.__name__}: {duration:.4f}s")

    return wrapper

class BenchmarkMixin:
    """Mixin class to add benchmark assertion capabilities to TestCase."""

    def assertExecutionTime(self, func: Callable, max_seconds: float, *args, **kwargs) -> float:
        """Assert that a function executes within a specified time limit.

        Args:
            func: The callable to test.
            max_seconds: The maximum allowed execution time in seconds.
            *args: Positional arguments for func.
            **kwargs: Keyword arguments for func.

        Returns:
            The execution time in seconds.

        Raises:
            AssertionError: If execution time exceeds max_seconds.
        """
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()

        duration = end_time - start_time

        if duration > max_seconds:
            self.fail(
                f"Performance check failed: {func.__name__} took {duration:.4f}s "
                f"(limit: {max_seconds:.4f}s)"
            )

        return duration
