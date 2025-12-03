"""Pydantic models for evaluation report representation.

Models for representing evaluation results, compliance status, and reports.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from jra.models.violation import Violation, ViolationSeverity


class ComplianceResult(BaseModel):
    """Model representing compliance evaluation results."""

    is_compliant: bool = Field(..., description="Whether ticket is fully compliant")
    violations: List[Violation] = Field(
        default_factory=list, description="List of violations found"
    )
    total_violations: int = Field(..., description="Total number of violations")
    critical_violations: int = Field(default=0, description="Number of critical violations")
    high_violations: int = Field(default=0, description="Number of high severity violations")
    medium_violations: int = Field(default=0, description="Number of medium severity violations")
    low_violations: int = Field(default=0, description="Number of low severity violations")
    compliance_score: float = Field(..., ge=0.0, le=100.0, description="Compliance score (0-100)")

    @field_validator("compliance_score")
    @classmethod
    def score_in_range(cls, v: float) -> float:
        """Validate compliance score is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError("Compliance score must be between 0 and 100")
        return round(v, 2)  # Round to 2 decimal places

    class Config:
        """Pydantic configuration."""

        frozen = False
        validate_assignment = True

    def calculate_severity_counts(self) -> None:
        """Calculate violation counts by severity level."""
        self.critical_violations = sum(
            1 for v in self.violations if v.severity == ViolationSeverity.CRITICAL
        )
        self.high_violations = sum(
            1 for v in self.violations if v.severity == ViolationSeverity.HIGH
        )
        self.medium_violations = sum(
            1 for v in self.violations if v.severity == ViolationSeverity.MEDIUM
        )
        self.low_violations = sum(1 for v in self.violations if v.severity == ViolationSeverity.LOW)
        self.total_violations = len(self.violations)

    def has_blocking_violations(self) -> bool:
        """Check if there are any blocking (CRITICAL or HIGH) violations.

        Returns:
            True if blocking violations exist
        """
        return self.critical_violations > 0 or self.high_violations > 0

    def get_violations_by_severity(self, severity: ViolationSeverity) -> List[Violation]:
        """Get violations filtered by severity level.

        Args:
            severity: Severity level to filter by

        Returns:
            List of violations with specified severity
        """
        return [v for v in self.violations if v.severity == severity]

    def get_violations_by_field(self, field_name: str) -> List[Violation]:
        """Get violations for a specific field.

        Args:
            field_name: Field name to filter by

        Returns:
            List of violations for the specified field
        """
        return [v for v in self.violations if v.field.lower() == field_name.lower()]


class EvaluationMetadata(BaseModel):
    """Metadata about the evaluation process."""

    evaluated_at: datetime = Field(..., description="Evaluation timestamp")
    duration_ms: Optional[float] = Field(None, description="Evaluation duration in milliseconds")
    guidelines_version: Optional[str] = Field(None, description="Guidelines version used")
    evaluator_version: str = Field(default="1.0.0", description="Evaluator version")

    class Config:
        """Pydantic configuration."""

        frozen = False


class EvaluationReport(BaseModel):
    """Complete evaluation report model.

    Represents the complete evaluation results for a Jira ticket.
    """

    # Ticket identification
    ticket_key: str = Field(..., description="Jira ticket key (e.g., PROJ-123)")

    # Evaluation timestamp
    evaluated_at: datetime = Field(..., description="When evaluation was performed")

    # Compliance results
    compliance: ComplianceResult = Field(..., description="Compliance evaluation results")

    # Optional metadata
    metadata: Optional[EvaluationMetadata] = Field(None, description="Evaluation metadata")

    # Optional summary
    summary: Optional[str] = Field(None, description="Executive summary of evaluation")

    class Config:
        """Pydantic configuration."""

        frozen = False
        validate_assignment = True

    @field_validator("ticket_key")
    @classmethod
    def validate_ticket_key(cls, v: str) -> str:
        """Validate ticket key format."""
        if not v or "-" not in v:
            raise ValueError("Ticket key must be in format PROJECT-NUMBER")
        return v

    def is_pass(self) -> bool:
        """Check if evaluation passes (is compliant).

        Returns:
            True if ticket is compliant
        """
        return self.compliance.is_compliant

    def is_fail(self) -> bool:
        """Check if evaluation fails (is not compliant).

        Returns:
            True if ticket is not compliant
        """
        return not self.compliance.is_compliant

    def get_score(self) -> float:
        """Get compliance score.

        Returns:
            Compliance score (0-100)
        """
        return self.compliance.compliance_score

    def get_violation_count(self) -> int:
        """Get total violation count.

        Returns:
            Total number of violations
        """
        return self.compliance.total_violations

    def has_critical_violations(self) -> bool:
        """Check if report has critical violations.

        Returns:
            True if critical violations exist
        """
        return self.compliance.critical_violations > 0

    def get_grade(self) -> str:
        """Get letter grade based on compliance score.

        Returns:
            Letter grade (A, B, C, D, F)
        """
        score = self.compliance.compliance_score

        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

    def to_dict(self) -> dict:
        """Convert report to dictionary with serializable values.

        Returns:
            Dictionary representation
        """
        return {
            "ticket_key": self.ticket_key,
            "evaluated_at": self.evaluated_at.isoformat(),
            "compliance": {
                "is_compliant": self.compliance.is_compliant,
                "total_violations": self.compliance.total_violations,
                "critical_violations": self.compliance.critical_violations,
                "high_violations": self.compliance.high_violations,
                "medium_violations": self.compliance.medium_violations,
                "low_violations": self.compliance.low_violations,
                "compliance_score": self.compliance.compliance_score,
                "violations": [v.to_dict() for v in self.compliance.violations],
            },
            "summary": self.summary,
            "metadata": (
                {
                    "evaluated_at": self.metadata.evaluated_at.isoformat(),
                    "duration_ms": self.metadata.duration_ms,
                    "guidelines_version": self.metadata.guidelines_version,
                    "evaluator_version": self.metadata.evaluator_version,
                }
                if self.metadata
                else None
            ),
        }
