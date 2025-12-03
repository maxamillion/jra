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
        self._elapsed: float | None = None

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
    def start_time(self) -> float | None:
        """Get start time.

        Returns:
            Start time or None if not started
        """
        return self._start_time

    @property
    def end_time(self) -> float | None:
        """Get end time.

        Returns:
            End time or None if not stopped
        """
        return self._end_time

    @property
    def elapsed(self) -> float | None:
        """Get elapsed time.

        Returns:
            Elapsed time in seconds or None if not stopped
        """
        if self._start_time is None:
            return None

        if self._end_time is None:
            # Timer still running - return None to match test expectations
            return None

        return self._elapsed

    def reset(self) -> None:
        """Reset the timer."""
        self._start_time = None
        self._end_time = None
        self._elapsed = None


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


def format_duration(seconds: float | None) -> str:
    """Format duration in human-readable form.

    Args:
        seconds: Duration in seconds (None if timer not stopped)

    Returns:
        Formatted duration string
    """
    if seconds is None:
        return "N/A"
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f}µs"
    elif seconds < 0.5:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"
