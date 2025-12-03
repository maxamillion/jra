"""Unit tests for data models.

Tests for Pydantic models: Jira, Guidelines, Violations, and Reports.
Per constitution: TDD is NON-NEGOTIABLE - comprehensive model validation required.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from jra.models import (
    ComplianceResult,
    EvaluationReport,
    FieldValidation,
    JiraIssue,
    ProcessGuidelines,
    RequiredField,
    Violation,
    ViolationCategory,
    ViolationSeverity,
    WorkflowRule,
)
from jra.models.jira import Component, IssueType, Priority, Project, Status, User


class TestJiraIssueValidation:
    """Test suite for Jira issue model validation.

    T034: Write unit tests for Jira models.
    """

    def test_create_minimal_valid_issue(self) -> None:
        """Test creating issue with minimal required fields."""
        issue = JiraIssue(
            id="10001",
            key="PROJ-123",
            summary="Test summary",
            issue_type=IssueType(name="Story"),
            status=Status(name="To Do"),
            project=Project(key="PROJ"),
            reporter=User(display_name="John Doe"),
        )

        assert issue.id == "10001"
        assert issue.key == "PROJ-123"
        assert issue.summary == "Test summary"

    def test_issue_key_validation(self) -> None:
        """Test issue key format validation."""
        # Valid key
        issue = JiraIssue(
            id="10001",
            key="PROJ-123",
            summary="Test",
            issue_type=IssueType(name="Story"),
            status=Status(name="To Do"),
            project=Project(key="PROJ"),
            reporter=User(display_name="John"),
        )
        assert issue.key == "PROJ-123"

        # Invalid key (no dash)
        with pytest.raises(ValidationError, match="format PROJECT-NUMBER"):
            JiraIssue(
                id="10001",
                key="INVALID",
                summary="Test",
                issue_type=IssueType(name="Story"),
                status=Status(name="To Do"),
                project=Project(key="PROJ"),
                reporter=User(display_name="John"),
            )

    def test_summary_validation(self) -> None:
        """Test summary cannot be empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            JiraIssue(
                id="10001",
                key="PROJ-123",
                summary="   ",  # Empty after strip
                issue_type=IssueType(name="Story"),
                status=Status(name="To Do"),
                project=Project(key="PROJ"),
                reporter=User(display_name="John"),
            )

    def test_issue_with_optional_fields(self) -> None:
        """Test creating issue with optional fields."""
        issue = JiraIssue(
            id="10001",
            key="PROJ-123",
            summary="Test summary",
            description="Detailed description",
            issue_type=IssueType(name="Story"),
            status=Status(name="To Do"),
            priority=Priority(name="High"),
            project=Project(key="PROJ"),
            reporter=User(display_name="John Doe", email_address="john@example.com"),
            assignee=User(display_name="Jane Smith"),
            labels=["backend", "urgent"],
            components=[Component(name="API")],
        )

        assert issue.description == "Detailed description"
        assert issue.priority.name == "High"
        assert issue.assignee.display_name == "Jane Smith"
        assert "backend" in issue.labels
        assert len(issue.components) == 1

    def test_issue_helper_methods(self) -> None:
        """Test issue model helper methods."""
        issue = JiraIssue(
            id="10001",
            key="PROJ-123",
            summary="Test",
            description="  ",
            issue_type=IssueType(name="Story"),
            status=Status(name="In Progress"),
            priority=Priority(name="Medium"),
            project=Project(key="PROJ"),
            reporter=User(display_name="John"),
            labels=["backend", "api"],
        )

        assert issue.get_issue_type_name() == "Story"
        assert issue.get_status_name() == "In Progress"
        assert issue.get_priority_name() == "Medium"
        assert not issue.has_description()  # Empty description
        assert not issue.has_assignee()
        assert issue.has_label("backend")
        assert not issue.has_label("frontend")

    def test_custom_fields_handling(self) -> None:
        """Test custom fields are preserved."""
        issue = JiraIssue(
            id="10001",
            key="PROJ-123",
            summary="Test",
            issue_type=IssueType(name="Story"),
            status=Status(name="To Do"),
            project=Project(key="PROJ"),
            reporter=User(display_name="John"),
            custom_fields={"customfield_10001": "Custom value", "customfield_10002": 42},
        )

        assert issue.get_custom_field("customfield_10001") == "Custom value"
        assert issue.get_custom_field("customfield_10002") == 42
        assert issue.get_custom_field("nonexistent", "default") == "default"


class TestProcessGuidelinesValidation:
    """Test suite for process guidelines model validation.

    T035: Write unit tests for Guidelines models.
    """

    def test_create_empty_guidelines(self) -> None:
        """Test creating guidelines with no rules."""
        guidelines = ProcessGuidelines()

        assert guidelines.required_fields == []
        assert guidelines.field_validations == []
        assert guidelines.workflow_rules == []

    def test_create_guidelines_with_required_fields(self) -> None:
        """Test creating guidelines with required fields."""
        guidelines = ProcessGuidelines(
            required_fields=[
                RequiredField(field_name="summary", issue_type=None),
                RequiredField(field_name="story_points", issue_type="Story"),
            ]
        )

        assert len(guidelines.required_fields) == 2
        assert guidelines.get_required_fields_for_type("Story") == guidelines.required_fields
        assert len(guidelines.get_required_fields_for_type("Bug")) == 1  # Only universal

    def test_create_guidelines_with_field_validations(self) -> None:
        """Test creating guidelines with field validation rules."""
        guidelines = ProcessGuidelines(
            field_validations=[
                FieldValidation(
                    field_name="summary",
                    rules=["Must be descriptive"],
                    min_length=10,
                    max_length=120,
                )
            ]
        )

        validation = guidelines.get_validation_for_field("summary")
        assert validation is not None
        assert validation.min_length == 10
        assert validation.max_length == 120

    def test_create_guidelines_with_workflow_rules(self) -> None:
        """Test creating guidelines with workflow transition rules."""
        guidelines = ProcessGuidelines(
            workflow_rules=[
                WorkflowRule(
                    from_status="To Do",
                    to_status="In Progress",
                    required_fields=["assignee"],
                ),
                WorkflowRule(
                    from_status="In Progress",
                    to_status="Done",
                    required_fields=["resolution"],
                ),
            ]
        )

        transitions = guidelines.get_workflow_transitions_from("To Do")
        assert len(transitions) == 1
        assert transitions[0].to_status == "In Progress"

        rule = guidelines.get_workflow_rule("In Progress", "Done")
        assert rule is not None
        assert "resolution" in rule.required_fields

    def test_guidelines_helper_methods(self) -> None:
        """Test guidelines model helper methods."""
        guidelines = ProcessGuidelines(
            sections={"Overview": "Guidelines overview", "Required Fields": "Field list"},
            field_validations=[FieldValidation(field_name="description", rules=["Required"])],
        )

        assert guidelines.has_section("Overview")
        assert not guidelines.has_section("Nonexistent")
        assert "overview" in guidelines.get_section("Overview").lower()
        assert guidelines.get_section("Missing", "default") == "default"

        validation = guidelines.get_validation_for_field("DESCRIPTION")  # Case insensitive
        assert validation is not None
        assert validation.field_name == "description"


class TestEvaluationReportValidation:
    """Test suite for evaluation report model validation.

    T036: Write unit tests for Report models.
    """

    def test_create_compliant_report(self) -> None:
        """Test creating report for compliant ticket."""
        compliance = ComplianceResult(
            is_compliant=True,
            violations=[],
            total_violations=0,
            critical_violations=0,
            compliance_score=100.0,
        )

        report = EvaluationReport(
            ticket_key="PROJ-123",
            evaluated_at=datetime(2025, 11, 26, 10, 0, 0),
            compliance=compliance,
        )

        assert report.is_pass()
        assert not report.is_fail()
        assert report.get_score() == 100.0
        assert report.get_grade() == "A"
        assert report.get_violation_count() == 0

    def test_create_non_compliant_report(self) -> None:
        """Test creating report for non-compliant ticket."""
        violations = [
            Violation(
                field="summary",
                message="Too short",
                severity=ViolationSeverity.MEDIUM,
                category=ViolationCategory.FIELD_VALIDATION,
            ),
            Violation(
                field="description",
                message="Missing acceptance criteria",
                severity=ViolationSeverity.HIGH,
                category=ViolationCategory.REQUIRED_FIELD,
            ),
        ]

        compliance = ComplianceResult(
            is_compliant=False,
            violations=violations,
            total_violations=2,
            critical_violations=0,
            high_violations=1,
            medium_violations=1,
            compliance_score=65.0,
        )

        report = EvaluationReport(
            ticket_key="PROJ-123",
            evaluated_at=datetime(2025, 11, 26, 10, 0, 0),
            compliance=compliance,
        )

        assert not report.is_pass()
        assert report.is_fail()
        assert report.get_score() == 65.0
        assert report.get_grade() == "C"
        assert report.get_violation_count() == 2

    def test_compliance_score_validation(self) -> None:
        """Test compliance score must be 0-100."""
        # Valid score
        compliance = ComplianceResult(
            is_compliant=False,
            violations=[],
            total_violations=0,
            compliance_score=75.5,
        )
        assert compliance.compliance_score == 75.5

        # Invalid score (too high)
        with pytest.raises(ValidationError):
            ComplianceResult(
                is_compliant=False,
                violations=[],
                total_violations=0,
                compliance_score=150.0,
            )

    def test_compliance_severity_counts(self) -> None:
        """Test compliance result calculates severity counts correctly."""
        violations = [
            Violation(
                field="f1",
                message="msg",
                severity=ViolationSeverity.CRITICAL,
                category=ViolationCategory.REQUIRED_FIELD,
            ),
            Violation(
                field="f2",
                message="msg",
                severity=ViolationSeverity.HIGH,
                category=ViolationCategory.REQUIRED_FIELD,
            ),
            Violation(
                field="f3",
                message="msg",
                severity=ViolationSeverity.HIGH,
                category=ViolationCategory.FIELD_VALIDATION,
            ),
            Violation(
                field="f4",
                message="msg",
                severity=ViolationSeverity.MEDIUM,
                category=ViolationCategory.FORMATTING,
            ),
        ]

        compliance = ComplianceResult(
            is_compliant=False,
            violations=violations,
            total_violations=0,  # Will be calculated
            compliance_score=50.0,
        )

        compliance.calculate_severity_counts()

        assert compliance.total_violations == 4
        assert compliance.critical_violations == 1
        assert compliance.high_violations == 2
        assert compliance.medium_violations == 1
        assert compliance.low_violations == 0

    def test_compliance_blocking_violations(self) -> None:
        """Test detection of blocking violations."""
        # No blocking violations
        compliance1 = ComplianceResult(
            is_compliant=False,
            violations=[],
            total_violations=0,
            critical_violations=0,
            high_violations=0,
            compliance_score=80.0,
        )
        assert not compliance1.has_blocking_violations()

        # Has blocking violations
        compliance2 = ComplianceResult(
            is_compliant=False,
            violations=[],
            total_violations=1,
            critical_violations=1,
            compliance_score=50.0,
        )
        assert compliance2.has_blocking_violations()

    def test_report_grade_calculation(self) -> None:
        """Test report grade calculation."""
        test_cases = [
            (95.0, "A"),
            (85.0, "B"),
            (70.0, "C"),
            (55.0, "D"),
            (40.0, "F"),
        ]

        for score, expected_grade in test_cases:
            compliance = ComplianceResult(
                is_compliant=(score == 100.0),
                violations=[],
                total_violations=0,
                compliance_score=score,
            )
            report = EvaluationReport(
                ticket_key="PROJ-123",
                evaluated_at=datetime.now(),
                compliance=compliance,
            )
            assert report.get_grade() == expected_grade

    def test_report_to_dict_serialization(self) -> None:
        """Test report serialization to dictionary."""
        violations = [
            Violation(
                field="summary",
                message="Test",
                severity=ViolationSeverity.MEDIUM,
                category=ViolationCategory.FIELD_VALIDATION,
            )
        ]

        compliance = ComplianceResult(
            is_compliant=False,
            violations=violations,
            total_violations=1,
            compliance_score=75.0,
        )

        report = EvaluationReport(
            ticket_key="PROJ-123",
            evaluated_at=datetime(2025, 11, 26, 10, 0, 0),
            compliance=compliance,
        )

        data = report.to_dict()

        assert data["ticket_key"] == "PROJ-123"
        assert data["compliance"]["total_violations"] == 1
        assert data["compliance"]["compliance_score"] == 75.0
        assert len(data["compliance"]["violations"]) == 1


class TestViolationModel:
    """Test suite for violation model."""

    def test_create_violation(self) -> None:
        """Test creating a violation."""
        violation = Violation(
            field="summary",
            message="Summary is too short",
            severity=ViolationSeverity.MEDIUM,
            category=ViolationCategory.FIELD_VALIDATION,
            reference="Section 2.1",
            suggestion="Make summary at least 10 characters",
        )

        assert violation.field == "summary"
        assert violation.severity == ViolationSeverity.MEDIUM
        assert violation.category == ViolationCategory.FIELD_VALIDATION

    def test_violation_is_blocking(self) -> None:
        """Test violation blocking status."""
        critical = Violation(
            field="test",
            message="msg",
            severity=ViolationSeverity.CRITICAL,
            category=ViolationCategory.REQUIRED_FIELD,
        )
        assert critical.is_blocking()

        low = Violation(
            field="test",
            message="msg",
            severity=ViolationSeverity.LOW,
            category=ViolationCategory.FORMATTING,
        )
        assert not low.is_blocking()

    def test_violation_severity_score(self) -> None:
        """Test violation severity scoring."""
        critical = Violation(
            field="test",
            message="msg",
            severity=ViolationSeverity.CRITICAL,
            category=ViolationCategory.REQUIRED_FIELD,
        )
        assert critical.get_severity_score() == 100

        medium = Violation(
            field="test",
            message="msg",
            severity=ViolationSeverity.MEDIUM,
            category=ViolationCategory.FIELD_VALIDATION,
        )
        assert medium.get_severity_score() == 50

    def test_violation_format_message(self) -> None:
        """Test violation message formatting."""
        violation = Violation(
            field="summary",
            message="Too short",
            severity=ViolationSeverity.HIGH,
            category=ViolationCategory.FIELD_VALIDATION,
            reference="Section 2.1",
            current_value="Bug",
            expected_value="At least 10 characters",
            suggestion="Add more detail",
        )

        formatted = violation.format_message()

        assert "[HIGH]" in formatted
        assert "summary" in formatted
        assert "Too short" in formatted
        assert "Section 2.1" in formatted
        assert "Bug" in formatted

    def test_violation_to_dict(self) -> None:
        """Test violation dictionary serialization."""
        violation = Violation(
            field="description",
            message="Missing acceptance criteria",
            severity=ViolationSeverity.HIGH,
            category=ViolationCategory.REQUIRED_FIELD,
        )

        data = violation.to_dict()

        assert data["field"] == "description"
        assert data["severity"] == "HIGH"
        assert data["category"] == "REQUIRED_FIELD"
