"""Unit tests for utility modules.

Tests for configuration, logging, timing, and exception handling utilities.
Per constitution: TDD is NON-NEGOTIABLE, ≥80% unit test coverage required.
"""

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from jra.utils.config import Config
from jra.utils.exceptions import (
    ConfigurationError,
    EvaluationError,
    GuidelineParseError,
    JiraParseError,
    JRAException,
    OutputError,
    ParseError,
    ValidationError,
)
from jra.utils.logging import setup_logging
from jra.utils.timing import Timer, format_duration, timed_operation


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfig:
    """Test suite for configuration management."""

    def test_default_config_structure(self) -> None:
        """Test that default configuration has required structure."""
        config = Config()

        assert "evaluation" in config.config
        assert "quality" in config.config
        assert "output" in config.config
        assert "batch" in config.config

    def test_default_evaluation_settings(self) -> None:
        """Test default evaluation configuration values."""
        config = Config()

        assert config.get("evaluation.strict_mode") is False
        assert config.get("evaluation.default_format") == "human"
        assert config.get("evaluation.enable_color") is True
        assert config.get("evaluation.show_timing") is False

    def test_default_quality_settings(self) -> None:
        """Test default quality configuration values."""
        config = Config()

        # Check weights sum to 1.0
        weights = [
            config.get("quality.completeness_weight"),
            config.get("quality.clarity_weight"),
            config.get("quality.formatting_weight"),
            config.get("quality.standards_weight"),
        ]
        assert abs(sum(weights) - 1.0) < 0.001  # Allow floating point tolerance

        # Check thresholds
        thresholds = config.get("quality.thresholds")
        assert thresholds["excellent"] == 90.0
        assert thresholds["good"] == 75.0
        assert thresholds["acceptable"] == 60.0
        assert thresholds["poor"] == 0.0

    def test_get_nested_key(self) -> None:
        """Test retrieving nested configuration values."""
        config = Config()

        # Nested key with dot notation
        assert config.get("quality.thresholds.excellent") == 90.0
        assert config.get("batch.max_workers") == 4
        assert config.get("output.indent") == 2

    def test_get_with_default(self) -> None:
        """Test retrieving non-existent keys with default values."""
        config = Config()

        assert config.get("nonexistent.key", "default") == "default"
        assert config.get("also.missing", 42) == 42
        assert config.get("missing") is None

    def test_set_value(self) -> None:
        """Test setting configuration values."""
        config = Config()

        config.set("custom.setting", "value")
        assert config.get("custom.setting") == "value"

        config.set("nested.deep.value", 123)
        assert config.get("nested.deep.value") == 123

    def test_update_existing_value(self) -> None:
        """Test updating existing configuration values."""
        config = Config()

        original = config.get("evaluation.strict_mode")
        config.set("evaluation.strict_mode", not original)
        assert config.get("evaluation.strict_mode") == (not original)

    @patch("builtins.open", new_callable=mock_open, read_data="[jra]\nstrict_mode = true\n")
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_from_file(self, mock_exists: MagicMock, mock_file: MagicMock) -> None:
        """Test loading configuration from TOML file."""
        config = Config()
        config.load_from_file(Path("test.toml"))

        # Verify file was opened
        mock_file.assert_called()

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_from_nonexistent_file(self, mock_exists: MagicMock) -> None:
        """Test loading from non-existent file raises error."""
        config = Config()

        with pytest.raises(ConfigurationError, match="not found"):
            config.load_from_file(Path("nonexistent.toml"))

    def test_load_from_env_vars(self) -> None:
        """Test loading configuration from environment variables."""
        config = Config()

        # Set environment variables
        os.environ["JRA_EVALUATION_STRICT_MODE"] = "true"
        os.environ["JRA_OUTPUT_INDENT"] = "4"

        config.load_from_env()

        assert config.get("evaluation.strict_mode") is True
        assert config.get("output.indent") == 4

        # Cleanup
        del os.environ["JRA_EVALUATION_STRICT_MODE"]
        del os.environ["JRA_OUTPUT_INDENT"]

    def test_as_dict(self) -> None:
        """Test converting configuration to dictionary."""
        config = Config()
        config_dict = config.as_dict()

        assert isinstance(config_dict, dict)
        assert "evaluation" in config_dict
        assert "quality" in config_dict


# ============================================================================
# Logging Tests
# ============================================================================


class TestLogging:
    """Test suite for logging utilities."""

    def test_setup_logging_default_level(self) -> None:
        """Test setting up logging with default INFO level."""
        logger = setup_logging()

        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logging_debug_level(self) -> None:
        """Test setting up logging with DEBUG level."""
        logger = setup_logging(level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_setup_logging_custom_format(self) -> None:
        """Test setting up logging with custom format."""
        custom_format = "%(levelname)s - %(message)s"
        logger = setup_logging(format_string=custom_format)

        assert len(logger.handlers) > 0
        handler = logger.handlers[0]
        assert handler.formatter is not None

    def test_logging_to_file(self, tmp_path: Path) -> None:
        """Test logging to a file."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=log_file)

        # Find file handler
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

    def test_log_message_output(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that log messages are captured correctly."""
        logger = setup_logging(level="INFO")

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert "Test message" in caplog.text


# ============================================================================
# Timing Tests
# ============================================================================


class TestTimer:
    """Test suite for timing utilities."""

    def test_timer_initialization(self) -> None:
        """Test timer initialization state."""
        timer = Timer()

        assert timer.start_time is None
        assert timer.end_time is None
        assert timer.elapsed is None

    def test_timer_start(self) -> None:
        """Test starting a timer."""
        timer = Timer()
        timer.start()

        assert timer.start_time is not None
        assert timer.end_time is None

    def test_timer_stop(self) -> None:
        """Test stopping a timer."""
        timer = Timer()
        timer.start()
        time.sleep(0.01)  # Small delay
        timer.stop()

        assert timer.start_time is not None
        assert timer.end_time is not None
        assert timer.elapsed is not None
        assert timer.elapsed > 0

    def test_timer_elapsed_calculation(self) -> None:
        """Test elapsed time calculation."""
        timer = Timer()
        timer.start()
        time.sleep(0.05)  # 50ms delay
        timer.stop()

        # Should be approximately 50ms (allow tolerance)
        assert 0.04 < timer.elapsed < 0.1

    def test_timer_reset(self) -> None:
        """Test resetting a timer."""
        timer = Timer()
        timer.start()
        timer.stop()
        timer.reset()

        assert timer.start_time is None
        assert timer.end_time is None
        assert timer.elapsed is None

    def test_format_duration_seconds(self) -> None:
        """Test formatting duration in seconds."""
        assert format_duration(1.234) == "1.23s"
        assert format_duration(0.5) == "0.50s"

    def test_format_duration_milliseconds(self) -> None:
        """Test formatting duration in milliseconds."""
        assert format_duration(0.123) == "123.00ms"
        assert format_duration(0.001) == "1.00ms"

    def test_format_duration_minutes(self) -> None:
        """Test formatting duration in minutes."""
        assert format_duration(65.5) == "1m 5.50s"
        assert format_duration(125.0) == "2m 5.00s"

    def test_timed_operation_context_manager(self) -> None:
        """Test timed_operation context manager."""
        with timed_operation("test") as timer:
            time.sleep(0.01)
            assert timer.start_time is not None

        assert timer.end_time is not None
        assert timer.elapsed is not None
        assert timer.elapsed > 0

    def test_timed_operation_with_exception(self) -> None:
        """Test timed_operation context manager with exception."""
        with pytest.raises(ValueError):
            with timed_operation("test") as timer:
                assert timer.start_time is not None
                raise ValueError("Test error")

        # Timer should still be stopped even with exception
        assert timer.end_time is not None


# ============================================================================
# Exception Tests
# ============================================================================


class TestExceptions:
    """Test suite for custom exception hierarchy."""

    def test_jra_exception_base(self) -> None:
        """Test base JRAException."""
        exc = JRAException("Test error")

        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.context == {}

    def test_jra_exception_with_context(self) -> None:
        """Test JRAException with context."""
        context = {"file": "test.json", "line": 42}
        exc = JRAException("Test error", context=context)

        assert exc.message == "Test error"
        assert exc.context == context
        assert exc.context["file"] == "test.json"

    def test_parse_error_hierarchy(self) -> None:
        """Test ParseError is subclass of JRAException."""
        exc = ParseError("Parse failed")

        assert isinstance(exc, JRAException)
        assert isinstance(exc, ParseError)

    def test_jira_parse_error(self) -> None:
        """Test JiraParseError."""
        exc = JiraParseError("Invalid JSON", context={"field": "summary"})

        assert isinstance(exc, ParseError)
        assert isinstance(exc, JRAException)
        assert exc.message == "Invalid JSON"
        assert exc.context["field"] == "summary"

    def test_guideline_parse_error(self) -> None:
        """Test GuidelineParseError."""
        exc = GuidelineParseError("Invalid markdown")

        assert isinstance(exc, ParseError)
        assert exc.message == "Invalid markdown"

    def test_validation_error_hierarchy(self) -> None:
        """Test ValidationError hierarchy."""
        exc = ValidationError("Validation failed")

        assert isinstance(exc, JRAException)
        assert not isinstance(exc, ParseError)

    def test_evaluation_error(self) -> None:
        """Test EvaluationError."""
        exc = EvaluationError("Evaluation failed")

        assert isinstance(exc, JRAException)
        assert exc.message == "Evaluation failed"

    def test_output_error(self) -> None:
        """Test OutputError."""
        exc = OutputError("Output generation failed")

        assert isinstance(exc, JRAException)
        assert exc.message == "Output generation failed"

    def test_configuration_error(self) -> None:
        """Test ConfigurationError."""
        exc = ConfigurationError("Invalid config")

        assert isinstance(exc, JRAException)
        assert exc.message == "Invalid config"

    def test_exception_inheritance_chain(self) -> None:
        """Test complete exception inheritance chain."""
        # JiraParseError should be instance of all parent classes
        exc = JiraParseError("Test")

        assert isinstance(exc, JiraParseError)
        assert isinstance(exc, ParseError)
        assert isinstance(exc, JRAException)
        assert isinstance(exc, Exception)

    def test_exception_raising(self) -> None:
        """Test raising custom exceptions."""
        with pytest.raises(JiraParseError, match="Invalid ticket"):
            raise JiraParseError("Invalid ticket")

        with pytest.raises(GuidelineParseError, match="Bad format"):
            raise GuidelineParseError("Bad format")

        with pytest.raises(ValidationError, match="Failed validation"):
            raise ValidationError("Failed validation")
