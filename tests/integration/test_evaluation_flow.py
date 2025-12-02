"""Integration tests for complete evaluation flow.

End-to-end tests for the evaluation pipeline.
Per constitution: TDD is NON-NEGOTIABLE - these tests written BEFORE implementation.
"""

import json
from pathlib import Path


class TestViolationDetectionFlow:
    """Integration tests for violation detection workflow.

    T027: Write integration test for violation detection and reporting.
    Tests the complete flow from input parsing through evaluation to output.
    """

    def test_complete_evaluation_pipeline(self, fixtures_dir: Path) -> None:
        """Test complete evaluation pipeline from parsing to output."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.formatters.json_formatter import JSONFormatter
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        # Load fixtures
        ticket_path = fixtures_dir / "tickets" / "invalid-bug.json"
        guidelines_path = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"

        # Parse inputs
        jira_parser = JiraParser()
        with open(ticket_path) as f:
            ticket_data = json.load(f)
        jira_issue = jira_parser.parse(ticket_data)

        markdown_parser = MarkdownParser()
        guidelines_text = guidelines_path.read_text()
        process_guidelines = markdown_parser.parse(guidelines_text)

        # Evaluate
        evaluator = ComplianceEvaluator()
        report = evaluator.evaluate(jira_issue, process_guidelines)

        # Format output
        formatter = JSONFormatter()
        output = formatter.format(report)

        # Contract: Pipeline should produce valid JSON output
        result = json.loads(output)
        assert isinstance(result, dict)
        assert "compliance" in result

    def test_violation_detection_for_missing_fields(self, fixtures_dir: Path) -> None:
        """Test violation detection for missing required fields."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        # Load invalid ticket (missing fields)
        ticket_path = fixtures_dir / "tickets" / "edge-cases" / "minimal-story.json"
        guidelines_path = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"

        jira_parser = JiraParser()
        with open(ticket_path) as f:
            ticket_data = json.load(f)
        jira_issue = jira_parser.parse(ticket_data)

        markdown_parser = MarkdownParser()
        process_guidelines = markdown_parser.parse(guidelines_path.read_text())

        # Evaluate
        evaluator = ComplianceEvaluator()
        report = evaluator.evaluate(jira_issue, process_guidelines)

        # Contract: Should detect missing required fields
        assert report.compliance.total_violations > 0

        # Contract: Violations should include field information
        violation_fields = {v.field for v in report.compliance.violations}
        assert len(violation_fields) > 0

    def test_violation_severity_classification(self, fixtures_dir: Path) -> None:
        """Test violations are classified by severity correctly."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        ticket_path = fixtures_dir / "tickets" / "invalid-bug.json"
        guidelines_path = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"

        jira_parser = JiraParser()
        with open(ticket_path) as f:
            ticket_data = json.load(f)
        jira_issue = jira_parser.parse(ticket_data)

        markdown_parser = MarkdownParser()
        process_guidelines = markdown_parser.parse(guidelines_path.read_text())

        evaluator = ComplianceEvaluator()
        report = evaluator.evaluate(jira_issue, process_guidelines)

        # Contract: Violations should have severity levels
        if report.compliance.violations:
            for violation in report.compliance.violations:
                assert hasattr(violation, "severity")
                assert violation.severity is not None

    def test_violation_categorization(self, fixtures_dir: Path) -> None:
        """Test violations are categorized correctly."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        ticket_path = fixtures_dir / "tickets" / "invalid-bug.json"
        guidelines_path = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"

        jira_parser = JiraParser()
        with open(ticket_path) as f:
            ticket_data = json.load(f)
        jira_issue = jira_parser.parse(ticket_data)

        markdown_parser = MarkdownParser()
        process_guidelines = markdown_parser.parse(guidelines_path.read_text())

        evaluator = ComplianceEvaluator()
        report = evaluator.evaluate(jira_issue, process_guidelines)

        # Contract: Violations should have categories
        if report.compliance.violations:
            for violation in report.compliance.violations:
                assert hasattr(violation, "category")
                assert violation.category is not None

    def test_compliance_score_reflects_violations(self, fixtures_dir: Path) -> None:
        """Test compliance score accurately reflects violation count and severity."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        # Test with invalid ticket
        invalid_ticket_path = fixtures_dir / "tickets" / "invalid-bug.json"
        guidelines_path = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"

        jira_parser = JiraParser()
        markdown_parser = MarkdownParser()

        with open(invalid_ticket_path) as f:
            invalid_data = json.load(f)
        invalid_issue = jira_parser.parse(invalid_data)

        process_guidelines = markdown_parser.parse(guidelines_path.read_text())

        evaluator = ComplianceEvaluator()
        invalid_report = evaluator.evaluate(invalid_issue, process_guidelines)

        # Test with valid ticket
        valid_ticket_path = fixtures_dir / "tickets" / "valid-story.json"
        with open(valid_ticket_path) as f:
            valid_data = json.load(f)
        valid_issue = jira_parser.parse(valid_data)

        valid_report = evaluator.evaluate(valid_issue, process_guidelines)

        # Contract: Invalid ticket should have lower score than valid ticket
        assert invalid_report.compliance.compliance_score < valid_report.compliance.compliance_score

        # Contract: More violations should mean lower score
        if invalid_report.compliance.total_violations > valid_report.compliance.total_violations:
            assert (
                invalid_report.compliance.compliance_score
                < valid_report.compliance.compliance_score
            )

    def test_evaluation_with_unicode_content(self, fixtures_dir: Path) -> None:
        """Test evaluation handles Unicode content correctly."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        ticket_path = fixtures_dir / "tickets" / "edge-cases" / "unicode-content.json"
        guidelines_path = fixtures_dir / "guidelines" / "basic-guidelines.md"

        jira_parser = JiraParser()
        with open(ticket_path, encoding="utf-8") as f:
            ticket_data = json.load(f)
        jira_issue = jira_parser.parse(ticket_data)

        markdown_parser = MarkdownParser()
        process_guidelines = markdown_parser.parse(guidelines_path.read_text())

        # Contract: Should handle Unicode without errors
        evaluator = ComplianceEvaluator()
        report = evaluator.evaluate(jira_issue, process_guidelines)

        assert report is not None
        assert report.ticket_key == "PROJ-105"

    def test_evaluation_with_large_description(self, fixtures_dir: Path) -> None:
        """Test evaluation handles large description fields."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        ticket_path = fixtures_dir / "tickets" / "edge-cases" / "large-description.json"
        guidelines_path = fixtures_dir / "guidelines" / "basic-guidelines.md"

        jira_parser = JiraParser()
        with open(ticket_path) as f:
            ticket_data = json.load(f)
        jira_issue = jira_parser.parse(ticket_data)

        markdown_parser = MarkdownParser()
        process_guidelines = markdown_parser.parse(guidelines_path.read_text())

        # Contract: Should handle large descriptions without performance issues
        evaluator = ComplianceEvaluator()
        report = evaluator.evaluate(jira_issue, process_guidelines)

        assert report is not None
        assert report.ticket_key == "PROJ-107"

    def test_violation_references_include_guideline_sections(self, fixtures_dir: Path) -> None:
        """Test violations include references to guideline sections."""
        from jra.evaluators.compliance import ComplianceEvaluator
        from jra.parsers.jira_parser import JiraParser
        from jra.parsers.markdown_parser import MarkdownParser

        ticket_path = fixtures_dir / "tickets" / "invalid-bug.json"
        guidelines_path = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"

        jira_parser = JiraParser()
        with open(ticket_path) as f:
            ticket_data = json.load(f)
        jira_issue = jira_parser.parse(ticket_data)

        markdown_parser = MarkdownParser()
        process_guidelines = markdown_parser.parse(guidelines_path.read_text())

        evaluator = ComplianceEvaluator()
        report = evaluator.evaluate(jira_issue, process_guidelines)

        # Contract: Violations should reference guideline sections
        if report.compliance.violations:
            for violation in report.compliance.violations:
                assert hasattr(violation, "reference")
                # Reference may be None for some violations, but should be string when present
                if violation.reference is not None:
                    assert isinstance(violation.reference, str)
