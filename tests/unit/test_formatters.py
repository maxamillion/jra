"""Unit tests for formatter modules.

Contract tests for JSON and human-readable output formatting.
Per constitution: TDD is NON-NEGOTIABLE - these tests written BEFORE implementation.
"""

import json
from datetime import datetime
from typing import Any

import pytest


class TestJSONFormatterContract:
    """Contract tests for JSON output formatter.

    T025: Write contract test for evaluation report JSON output.
    These tests define the contract that the JSONFormatter must fulfill.
    """

    @pytest.fixture
    def sample_evaluation_report(self) -> Any:
        """Create a sample evaluation report for testing."""
        from jra.models.report import ComplianceResult, EvaluationReport, Violation
        from jra.models.violation import ViolationSeverity, ViolationCategory

        violations = [
            Violation(
                field="summary",
                message="Summary is too short",
                severity=ViolationSeverity.MEDIUM,
                category=ViolationCategory.REQUIRED_FIELD,
                reference="Section 2.1: Summary Validation",
            )
        ]

        compliance = ComplianceResult(
            is_compliant=False,
            violations=violations,
            total_violations=1,
            critical_violations=0,
            compliance_score=85.5,
        )

        report = EvaluationReport(
            ticket_key="PROJ-101",
            evaluated_at=datetime(2025, 11, 26, 10, 0, 0),
            compliance=compliance,
        )

        return report

    def test_format_produces_valid_json(self, sample_evaluation_report: Any) -> None:
        """Test formatter produces valid JSON output."""
        from jra.formatters.json_formatter import JSONFormatter

        formatter = JSONFormatter()
        output = formatter.format(sample_evaluation_report)

        # Contract: Must produce valid JSON string
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_format_includes_required_fields(self, sample_evaluation_report: Any) -> None:
        """Test formatted output includes all required fields."""
        from jra.formatters.json_formatter import JSONFormatter

        formatter = JSONFormatter()
        output = formatter.format(sample_evaluation_report)
        data = json.loads(output)

        # Contract: Must include ticket key
        assert "ticket_key" in data
        assert data["ticket_key"] == "PROJ-101"

        # Contract: Must include timestamp
        assert "evaluated_at" in data

        # Contract: Must include compliance results
        assert "compliance" in data
        assert "is_compliant" in data["compliance"]
        assert "compliance_score" in data["compliance"]

    def test_format_includes_violations_array(self, sample_evaluation_report: Any) -> None:
        """Test formatted output includes violations array."""
        from jra.formatters.json_formatter import JSONFormatter

        formatter = JSONFormatter()
        output = formatter.format(sample_evaluation_report)
        data = json.loads(output)

        # Contract: Must include violations array
        assert "compliance" in data
        assert "violations" in data["compliance"]
        assert isinstance(data["compliance"]["violations"], list)

        # Contract: Violations must have required fields
        if data["compliance"]["violations"]:
            violation = data["compliance"]["violations"][0]
            assert "field" in violation
            assert "message" in violation
            assert "severity" in violation
            assert "category" in violation

    def test_format_with_indent_option(self, sample_evaluation_report: Any) -> None:
        """Test formatter supports indent option for readability."""
        from jra.formatters.json_formatter import JSONFormatter

        formatter = JSONFormatter(indent=2)
        output = formatter.format(sample_evaluation_report)

        # Contract: Indented JSON should have newlines
        assert "\n" in output

        # Contract: Should still be valid JSON
        data = json.loads(output)
        assert data is not None

    def test_format_with_compact_option(self, sample_evaluation_report: Any) -> None:
        """Test formatter supports compact output."""
        from jra.formatters.json_formatter import JSONFormatter

        formatter = JSONFormatter(indent=None)
        output = formatter.format(sample_evaluation_report)

        # Contract: Compact JSON should minimize whitespace
        # (though it may have some minimal formatting)
        assert isinstance(output, str)
        data = json.loads(output)
        assert data is not None

    def test_format_handles_empty_violations(self) -> None:
        """Test formatter handles reports with no violations."""
        from jra.formatters.json_formatter import JSONFormatter
        from jra.models.report import ComplianceResult, EvaluationReport

        compliance = ComplianceResult(
            is_compliant=True,
            violations=[],
            total_violations=0,
            critical_violations=0,
            compliance_score=100.0,
        )

        report = EvaluationReport(
            ticket_key="PROJ-102",
            evaluated_at=datetime(2025, 11, 26, 10, 0, 0),
            compliance=compliance,
        )

        formatter = JSONFormatter()
        output = formatter.format(report)
        data = json.loads(output)

        # Contract: Must handle empty violations gracefully
        assert data["compliance"]["violations"] == []
        assert data["compliance"]["is_compliant"] is True


class TestHumanFormatterContract:
    """Contract tests for human-readable output formatter.

    T025: Write contract test for human-readable terminal output.
    These tests define the contract that the HumanFormatter must fulfill.
    """

    @pytest.fixture
    def sample_evaluation_report(self) -> Any:
        """Create a sample evaluation report for testing."""
        from jra.models.report import ComplianceResult, EvaluationReport, Violation
        from jra.models.violation import ViolationSeverity, ViolationCategory

        violations = [
            Violation(
                field="summary",
                message="Summary is too short (minimum 10 characters)",
                severity=ViolationSeverity.MEDIUM,
                category=ViolationCategory.REQUIRED_FIELD,
                reference="Section 2.1: Summary Validation",
            ),
            Violation(
                field="description",
                message="Missing acceptance criteria section",
                severity=ViolationSeverity.HIGH,
                category=ViolationCategory.FIELD_VALIDATION,
                reference="Section 2.2: Description Requirements",
            ),
        ]

        compliance = ComplianceResult(
            is_compliant=False,
            violations=violations,
            total_violations=2,
            critical_violations=0,
            compliance_score=75.0,
        )

        report = EvaluationReport(
            ticket_key="PROJ-101",
            evaluated_at=datetime(2025, 11, 26, 10, 0, 0),
            compliance=compliance,
        )

        return report

    def test_format_produces_string_output(self, sample_evaluation_report: Any) -> None:
        """Test formatter produces string output."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter()
        output = formatter.format(sample_evaluation_report)

        # Contract: Must produce string output
        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_includes_ticket_key(self, sample_evaluation_report: Any) -> None:
        """Test formatted output includes ticket key."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter()
        output = formatter.format(sample_evaluation_report)

        # Contract: Must include ticket key in output
        assert "PROJ-101" in output

    def test_format_includes_compliance_status(self, sample_evaluation_report: Any) -> None:
        """Test formatted output includes compliance status."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter()
        output = formatter.format(sample_evaluation_report)

        # Contract: Must include compliance status
        # (could be "Compliant", "Non-Compliant", "PASS", "FAIL", etc.)
        output_lower = output.lower()
        assert any(
            word in output_lower
            for word in ["compliant", "non-compliant", "pass", "fail", "✓", "✗", "✅", "❌"]
        )

    def test_format_includes_compliance_score(self, sample_evaluation_report: Any) -> None:
        """Test formatted output includes compliance score."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter()
        output = formatter.format(sample_evaluation_report)

        # Contract: Must include score (75.0% or similar)
        assert "75" in output

    def test_format_lists_violations(self, sample_evaluation_report: Any) -> None:
        """Test formatted output lists all violations."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter()
        output = formatter.format(sample_evaluation_report)

        # Contract: Must list violations with field and message
        assert "summary" in output.lower()
        assert "description" in output.lower()
        assert "too short" in output.lower()
        assert "acceptance criteria" in output.lower()

    def test_format_shows_severity_levels(self, sample_evaluation_report: Any) -> None:
        """Test formatted output shows violation severity."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter()
        output = formatter.format(sample_evaluation_report)

        # Contract: Must indicate severity (HIGH, MEDIUM, etc.)
        output_upper = output.upper()
        assert any(severity in output_upper for severity in ["HIGH", "MEDIUM", "LOW", "CRITICAL"])

    def test_format_with_color_option(self, sample_evaluation_report: Any) -> None:
        """Test formatter supports color output option."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter(use_color=True)
        output = formatter.format(sample_evaluation_report)

        # Contract: Color output should contain ANSI escape codes
        # (or at least produce valid output)
        assert isinstance(output, str)

    def test_format_without_color(self, sample_evaluation_report: Any) -> None:
        """Test formatter supports plain text output."""
        from jra.formatters.human_formatter import HumanFormatter

        formatter = HumanFormatter(use_color=False)
        output = formatter.format(sample_evaluation_report)

        # Contract: Plain output should not contain ANSI codes
        assert "\033[" not in output  # No ANSI escape sequences

    def test_format_handles_compliant_report(self) -> None:
        """Test formatter handles fully compliant reports."""
        from jra.formatters.human_formatter import HumanFormatter
        from jra.models.report import ComplianceResult, EvaluationReport

        compliance = ComplianceResult(
            is_compliant=True,
            violations=[],
            total_violations=0,
            critical_violations=0,
            compliance_score=100.0,
        )

        report = EvaluationReport(
            ticket_key="PROJ-102",
            evaluated_at=datetime(2025, 11, 26, 10, 0, 0),
            compliance=compliance,
        )

        formatter = HumanFormatter()
        output = formatter.format(report)

        # Contract: Must show positive compliance status
        output_lower = output.lower()
        assert any(word in output_lower for word in ["compliant", "pass", "✓", "✅", "100"])

        # Contract: Should indicate no violations
        assert any(word in output_lower for word in ["no violations", "0 violations", "clean"])
