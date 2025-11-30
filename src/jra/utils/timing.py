"""Performance timing utilities for JRA."""

import time
from contextlib import contextmanager
from typing import Generator


class Timer:
    """Simple timer for performance measurement."""

    def __init__(self) -> None:
        """Initialize timer."""
        self._start_time: float | None = None
        self._end_time: float | None = None
        self._elapsed: float = 0.0

    def start(self) -> None:
        """Start the timer."""
        self._start_time = time.perf_counter()
        self._end_time = None

    def stop(self) -> float:
        """Stop the timer and return elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self._start_time is None:
            raise RuntimeError("Timer not started")
        
        self._end_time = time.perf_counter()
        self._elapsed = self._end_time - self._start_time
        return self._elapsed

    @property
    def elapsed(self) -> float:
        """Get elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        if self._start_time is None:
            return 0.0
        
        if self._end_time is None:
            # Timer still running
            return time.perf_counter() - self._start_time
        
        return self._elapsed

    def reset(self) -> None:
        """Reset the timer."""
        self._start_time = None
        self._end_time = None
        self._elapsed = 0.0


@contextmanager
def timed_operation(operation_name: str = "operation") -> Generator[Timer, None, None]:
    """Context manager for timing operations.
    
    Args:
        operation_name: Name of the operation being timed
        
    Yields:
        Timer instance
        
    Example:
        >>> with timed_operation("evaluation") as timer:
        ...     # do work
        ...     pass
        >>> print(f"Took {timer.elapsed:.2f}s")
    """
    timer = Timer()
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()
