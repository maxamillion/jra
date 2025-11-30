"""Compliance evaluator implementation.

Evaluates Jira issues for compliance with process guidelines.
"""

from datetime import datetime
from typing import Any, List

from jra.evaluators.base import BaseEvaluator
from jra.models.guidelines import ProcessGuidelines
from jra.models.jira import JiraIssue
from jra.models.report import ComplianceResult, EvaluationReport
from jra.models.violation import Violation, ViolationCategory, ViolationSeverity
from jra.utils.exceptions import EvaluationError


class ComplianceEvaluator(BaseEvaluator):
    """Evaluator for process guidelines compliance.

    Checks required fields, field validations, and workflow rules.
    """

    def evaluate(self, issue: JiraIssue, guidelines: ProcessGuidelines) -> EvaluationReport:
        """Evaluate issue compliance against guidelines.

        Args:
            issue: Jira issue to evaluate
            guidelines: Process guidelines to check against

        Returns:
            Evaluation report with compliance results

        Raises:
            EvaluationError: If evaluation fails
        """
        try:
            violations: List[Violation] = []

            # Check required fields
            violations.extend(self._check_required_fields(issue, guidelines))

            # Check field validations
            violations.extend(self._check_field_validations(issue, guidelines))

            # Check workflow rules (if applicable)
            violations.extend(self._check_workflow_rules(issue, guidelines))

            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(violations)

            # Determine if compliant (no blocking violations)
            is_compliant = len(violations) == 0

            # Build compliance result
            compliance = ComplianceResult(
                is_compliant=is_compliant,
                violations=violations,
                total_violations=len(violations),
                compliance_score=compliance_score,
            )

            # Calculate severity counts
            compliance.calculate_severity_counts()

            # Create evaluation report
            report = EvaluationReport(
                ticket_key=issue.key,
                evaluated_at=datetime.now(),
                compliance=compliance,
            )

            return report

        except Exception as e:
            if isinstance(e, EvaluationError):
                raise
            raise EvaluationError(
                f"Compliance evaluation failed for {issue.key}: {str(e)}"
            ) from e

    def _check_required_fields(
        self, issue: JiraIssue, guidelines: ProcessGuidelines
    ) -> List[Violation]:
        """Check for missing required fields.

        Args:
            issue: Jira issue to check
            guidelines: Process guidelines

        Returns:
            List of violations for missing required fields
        """
        violations = []
        issue_type = issue.get_issue_type_name()

        # Get required fields for this issue type
        required_fields = guidelines.get_required_fields_for_type(issue_type)

        for required_field in required_fields:
            field_name = required_field.field_name.lower()

            # Check if field exists and has value
            is_missing = False

            if field_name == "summary":
                is_missing = not issue.has_description() if field_name == "description" else False
            elif field_name == "description":
                is_missing = not issue.has_description()
            elif field_name == "assignee":
                is_missing = not issue.has_assignee()
            elif field_name == "priority":
                is_missing = issue.priority is None
            elif field_name == "story points" or field_name == "story_points":
                # Check custom field for story points (commonly customfield_10004 or similar)
                story_points = issue.get_custom_field("story_points")
                if story_points is None:
                    # Try common custom field names
                    story_points = issue.get_custom_field("customfield_10004")
                is_missing = story_points is None
            elif field_name == "acceptance criteria":
                # Check if description contains acceptance criteria
                if issue.description:
                    is_missing = "acceptance criteria" not in issue.description.lower()
                else:
                    is_missing = True
            elif field_name in ["steps to reproduce", "expected behavior", "actual behavior"]:
                # Bug-specific fields in description
                if issue.description:
                    is_missing = field_name.replace("_", " ") not in issue.description.lower()
                else:
                    is_missing = True
            else:
                # Generic field check - look in custom fields
                custom_value = issue.get_custom_field(field_name.replace(" ", "_"))
                is_missing = custom_value is None

            if is_missing:
                violations.append(
                    Violation(
                        field=required_field.field_name,
                        message=f"Required field '{required_field.field_name}' is missing or empty",
                        severity=ViolationSeverity.HIGH,
                        category=ViolationCategory.REQUIRED_FIELD,
                        reference=f"Required Fields for {issue_type}" if required_field.issue_type else "Universal Required Fields",
                        suggestion=f"Add {required_field.field_name} to the ticket",
                    )
                )

        return violations

    def _check_field_validations(
        self, issue: JiraIssue, guidelines: ProcessGuidelines
    ) -> List[Violation]:
        """Check field validation rules.

        Args:
            issue: Jira issue to check
            guidelines: Process guidelines

        Returns:
            List of violations for field validation failures
        """
        violations = []

        # Validate summary
        summary_validation = guidelines.get_validation_for_field("summary")
        if summary_validation and issue.summary:
            violations.extend(self._validate_field("summary", issue.summary, summary_validation))

        # Validate description
        desc_validation = guidelines.get_validation_for_field("description")
        if desc_validation and issue.description:
            violations.extend(
                self._validate_field("description", issue.description, desc_validation)
            )

        # Validate priority
        priority_validation = guidelines.get_validation_for_field("priority")
        if priority_validation and issue.priority:
            violations.extend(
                self._validate_field("priority", issue.get_priority_name(), priority_validation)
            )

        return violations

    def _validate_field(
        self, field_name: str, field_value: str, validation: Any
    ) -> List[Violation]:
        """Validate a single field against its validation rules.

        Args:
            field_name: Name of the field
            field_value: Current field value
            validation: Field validation rules

        Returns:
            List of violations
        """
        violations = []

        # Check minimum length
        if validation.min_length and len(field_value) < validation.min_length:
            violations.append(
                Violation(
                    field=field_name,
                    message=f"Field is too short (minimum {validation.min_length} characters)",
                    severity=ViolationSeverity.MEDIUM,
                    category=ViolationCategory.FIELD_VALIDATION,
                    reference=f"{field_name.title()} Validation",
                    current_value=f"{len(field_value)} characters",
                    expected_value=f"≥{validation.min_length} characters",
                    suggestion=f"Expand {field_name} to at least {validation.min_length} characters",
                )
            )

        # Check maximum length
        if validation.max_length and len(field_value) > validation.max_length:
            violations.append(
                Violation(
                    field=field_name,
                    message=f"Field is too long (maximum {validation.max_length} characters)",
                    severity=ViolationSeverity.LOW,
                    category=ViolationCategory.FIELD_VALIDATION,
                    reference=f"{field_name.title()} Validation",
                    current_value=f"{len(field_value)} characters",
                    expected_value=f"≤{validation.max_length} characters",
                    suggestion=f"Shorten {field_name} to {validation.max_length} characters or less",
                )
            )

        # Check required sections
        if validation.required_sections:
            field_value_lower = field_value.lower()
            for section in validation.required_sections:
                section_lower = section.lower()
                if section_lower not in field_value_lower:
                    violations.append(
                        Violation(
                            field=field_name,
                            message=f"Missing required section: {section}",
                            severity=ViolationSeverity.MEDIUM,
                            category=ViolationCategory.FIELD_VALIDATION,
                            reference=f"{field_name.title()} Validation - Required Sections",
                            expected_value=section,
                            suggestion=f"Add '{section}' section to {field_name}",
                        )
                    )

        return violations

    def _check_workflow_rules(
        self, issue: JiraIssue, guidelines: ProcessGuidelines
    ) -> List[Violation]:
        """Check workflow transition rules (if applicable).

        Args:
            issue: Jira issue to check
            guidelines: Process guidelines

        Returns:
            List of violations for workflow rule failures
        """
        violations = []

        # Get current status
        current_status = issue.get_status_name()

        # Get valid transitions from current status
        valid_transitions = guidelines.get_workflow_transitions_from(current_status)

        # For now, we don't have historical transition data
        # This would require access to issue history/changelog
        # Placeholder for future enhancement

        return violations

    def _calculate_compliance_score(self, violations: List[Violation]) -> float:
        """Calculate compliance score based on violations.

        Args:
            violations: List of violations

        Returns:
            Compliance score (0-100)
        """
        if not violations:
            return 100.0

        # Calculate total deduction based on violation severity
        total_deduction = 0.0

        for violation in violations:
            if violation.severity == ViolationSeverity.CRITICAL:
                total_deduction += 25.0
            elif violation.severity == ViolationSeverity.HIGH:
                total_deduction += 15.0
            elif violation.severity == ViolationSeverity.MEDIUM:
                total_deduction += 8.0
            elif violation.severity == ViolationSeverity.LOW:
                total_deduction += 3.0
            elif violation.severity == ViolationSeverity.INFO:
                total_deduction += 1.0

        # Calculate score (ensure it doesn't go below 0)
        score = max(0.0, 100.0 - total_deduction)

        return round(score, 2)
