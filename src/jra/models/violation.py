"""Pydantic models for violation representation.

Models for representing guideline violations found during evaluation.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ViolationSeverity(str, Enum):
    """Violation severity levels."""

    CRITICAL = "CRITICAL"  # Blocks deployment, must fix immediately
    HIGH = "HIGH"  # Significant issue, should fix before merging
    MEDIUM = "MEDIUM"  # Important issue, should fix soon
    LOW = "LOW"  # Minor issue, can be addressed later
    INFO = "INFO"  # Informational, not blocking


class ViolationCategory(str, Enum):
    """Violation category classification."""

    REQUIRED_FIELD = "REQUIRED_FIELD"  # Missing required field
    FIELD_VALIDATION = "FIELD_VALIDATION"  # Field value doesn't meet validation rules
    WORKFLOW_RULE = "WORKFLOW_RULE"  # Workflow transition rule violation
    QUALITY_STANDARD = "QUALITY_STANDARD"  # Quality standard not met
    CUSTOM_RULE = "CUSTOM_RULE"  # Custom rule violation
    FORMATTING = "FORMATTING"  # Formatting or structure issue
    CONSISTENCY = "CONSISTENCY"  # Inconsistency with standards


class Violation(BaseModel):
    """Model representing a single guideline violation.

    Captures all information about a violation including what was violated,
    why it's a violation, and how severe it is.
    """

    field: str = Field(..., description="Field or aspect that violates guidelines")
    message: str = Field(..., description="Human-readable violation message")
    severity: ViolationSeverity = Field(..., description="Severity level of violation")
    category: ViolationCategory = Field(..., description="Category of violation")
    reference: Optional[str] = Field(
        None, description="Reference to guideline section (e.g., 'Section 2.1')"
    )
    current_value: Optional[str] = Field(None, description="Current field value (if applicable)")
    expected_value: Optional[str] = Field(
        None, description="Expected value or pattern (if applicable)"
    )
    suggestion: Optional[str] = Field(None, description="Suggestion for fixing the violation")

    class Config:
        """Pydantic configuration."""

        frozen = False
        use_enum_values = False  # Keep enum instances, don't convert to strings

    def is_blocking(self) -> bool:
        """Check if violation is blocking (CRITICAL or HIGH severity).

        Returns:
            True if violation should block progress
        """
        return self.severity in (ViolationSeverity.CRITICAL, ViolationSeverity.HIGH)

    def get_severity_score(self) -> int:
        """Get numeric score for severity (higher = more severe).

        Returns:
            Numeric severity score (0-100)
        """
        severity_scores = {
            ViolationSeverity.CRITICAL: 100,
            ViolationSeverity.HIGH: 75,
            ViolationSeverity.MEDIUM: 50,
            ViolationSeverity.LOW: 25,
            ViolationSeverity.INFO: 10,
        }
        return severity_scores.get(self.severity, 0)

    def format_message(self) -> str:
        """Format violation message with all context.

        Returns:
            Formatted violation message
        """
        parts = [f"[{self.severity.value}] {self.field}: {self.message}"]

        if self.reference:
            parts.append(f"(Reference: {self.reference})")

        if self.current_value:
            parts.append(f"Current: {self.current_value}")

        if self.expected_value:
            parts.append(f"Expected: {self.expected_value}")

        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")

        return " | ".join(parts)

    def to_dict(self) -> dict:
        """Convert violation to dictionary with enum values as strings.

        Returns:
            Dictionary representation with string enum values
        """
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "reference": self.reference,
            "current_value": self.current_value,
            "expected_value": self.expected_value,
            "suggestion": self.suggestion,
        }
