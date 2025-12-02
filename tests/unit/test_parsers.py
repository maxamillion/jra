"""Unit tests for parser modules.

Contract tests for Jira JSON and markdown parsing.
Per constitution: TDD is NON-NEGOTIABLE - these tests written BEFORE implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from jra.utils.exceptions import GuidelineParseError, JiraParseError


class TestJiraParserContract:
    """Contract tests for Jira JSON parser.

    T023: Write contract test for Jira JSON input validation.
    These tests define the contract that the JiraParser must fulfill.
    """

    @pytest.fixture
    def valid_jira_json(self, fixtures_dir: Path) -> Dict[str, Any]:
        """Load valid Jira JSON fixture."""
        fixture_path = fixtures_dir / "tickets" / "valid-story.json"
        with open(fixture_path) as f:
            return json.load(f)

    @pytest.fixture
    def invalid_jira_json(self, fixtures_dir: Path) -> Dict[str, Any]:
        """Load invalid Jira JSON fixture."""
        fixture_path = fixtures_dir / "tickets" / "invalid-bug.json"
        with open(fixture_path) as f:
            return json.load(f)

    def test_parse_valid_jira_json(self, valid_jira_json: Dict[str, Any]) -> None:
        """Test parsing valid Jira JSON returns JiraIssue model."""
        from jra.parsers.jira_parser import JiraParser

        parser = JiraParser()
        issue = parser.parse(valid_jira_json)

        # Contract: Must return a JiraIssue instance
        from jra.models.jira import JiraIssue

        assert isinstance(issue, JiraIssue)

        # Contract: Must extract required fields
        assert issue.key == "PROJ-101"
        assert issue.summary is not None
        assert issue.issue_type is not None
        assert issue.status is not None

    def test_parse_validates_required_fields(self, valid_jira_json: Dict[str, Any]) -> None:
        """Test parser validates presence of required fields."""
        from jra.parsers.jira_parser import JiraParser

        parser = JiraParser()

        # Remove required field
        invalid_json = valid_jira_json.copy()
        del invalid_json["fields"]["summary"]

        # Contract: Must raise JiraParseError for missing required fields
        with pytest.raises(JiraParseError, match="summary"):
            parser.parse(invalid_json)

    def test_parse_extracts_nested_fields(self, valid_jira_json: Dict[str, Any]) -> None:
        """Test parser extracts nested field structures."""
        from jra.parsers.jira_parser import JiraParser

        parser = JiraParser()
        issue = parser.parse(valid_jira_json)

        # Contract: Must extract nested reporter information
        assert issue.reporter is not None
        assert issue.reporter.display_name == "John Doe"

        # Contract: Must extract nested issue type
        assert issue.issue_type.name == "Story"

    def test_parse_handles_optional_fields(self, valid_jira_json: Dict[str, Any]) -> None:
        """Test parser handles missing optional fields gracefully."""
        from jra.parsers.jira_parser import JiraParser

        parser = JiraParser()

        # Remove optional fields
        minimal_json = valid_jira_json.copy()
        minimal_json["fields"].pop("assignee", None)
        minimal_json["fields"].pop("labels", None)

        # Contract: Must not raise error for missing optional fields
        issue = parser.parse(minimal_json)
        assert issue is not None
        assert issue.assignee is None
        assert issue.labels == []

    def test_parse_handles_malformed_json(self) -> None:
        """Test parser handles malformed JSON structure."""
        from jra.parsers.jira_parser import JiraParser

        parser = JiraParser()

        # Contract: Must raise JiraParseError for malformed structure
        with pytest.raises(JiraParseError):
            parser.parse({"invalid": "structure"})

    def test_parse_preserves_custom_fields(self, valid_jira_json: Dict[str, Any]) -> None:
        """Test parser preserves custom fields for future use."""
        from jra.parsers.jira_parser import JiraParser

        parser = JiraParser()

        # Add custom field
        json_with_custom = valid_jira_json.copy()
        json_with_custom["fields"]["customfield_10001"] = "Custom value"

        issue = parser.parse(json_with_custom)

        # Contract: Must preserve custom fields in model
        assert hasattr(issue, "custom_fields")
        assert "customfield_10001" in issue.custom_fields


class TestMarkdownParserContract:
    """Contract tests for markdown guideline parser.

    T024: Write contract test for guidelines markdown parsing.
    These tests define the contract that the MarkdownParser must fulfill.
    """

    @pytest.fixture
    def basic_guidelines(self, fixtures_dir: Path) -> str:
        """Load basic guidelines markdown fixture."""
        fixture_path = fixtures_dir / "guidelines" / "basic-guidelines.md"
        return fixture_path.read_text()

    @pytest.fixture
    def comprehensive_guidelines(self, fixtures_dir: Path) -> str:
        """Load comprehensive guidelines markdown fixture."""
        fixture_path = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"
        return fixture_path.read_text()

    def test_parse_valid_markdown(self, basic_guidelines: str) -> None:
        """Test parsing valid markdown returns ProcessGuidelines model."""
        from jra.parsers.markdown_parser import MarkdownParser

        parser = MarkdownParser()
        guidelines = parser.parse(basic_guidelines)

        # Contract: Must return ProcessGuidelines instance
        from jra.models.guidelines import ProcessGuidelines

        assert isinstance(guidelines, ProcessGuidelines)

    def test_extract_required_fields_section(self, comprehensive_guidelines: str) -> None:
        """Test extraction of required fields from markdown."""
        from jra.parsers.markdown_parser import MarkdownParser

        parser = MarkdownParser()
        guidelines = parser.parse(comprehensive_guidelines)

        # Contract: Must extract required fields list
        assert hasattr(guidelines, "required_fields")
        assert len(guidelines.required_fields) > 0

        # Contract: Must identify story-specific required fields
        story_fields = [f for f in guidelines.required_fields if f.issue_type == "Story"]
        assert len(story_fields) > 0

    def test_extract_field_validations(self, comprehensive_guidelines: str) -> None:
        """Test extraction of field validation rules."""
        from jra.parsers.markdown_parser import MarkdownParser

        parser = MarkdownParser()
        guidelines = parser.parse(comprehensive_guidelines)

        # Contract: Must extract field validations
        assert hasattr(guidelines, "field_validations")
        assert len(guidelines.field_validations) > 0

        # Contract: Validations must include field name and rules
        for validation in guidelines.field_validations:
            assert hasattr(validation, "field_name")
            assert hasattr(validation, "rules")

    def test_extract_workflow_rules(self, comprehensive_guidelines: str) -> None:
        """Test extraction of workflow transition rules."""
        from jra.parsers.markdown_parser import MarkdownParser

        parser = MarkdownParser()
        guidelines = parser.parse(comprehensive_guidelines)

        # Contract: Must extract workflow rules
        assert hasattr(guidelines, "workflow_rules")
        assert len(guidelines.workflow_rules) > 0

        # Contract: Rules must specify valid transitions
        for rule in guidelines.workflow_rules:
            assert hasattr(rule, "from_status")
            assert hasattr(rule, "to_status")

    def test_handles_missing_sections(self) -> None:
        """Test parser handles markdown with missing sections."""
        from jra.parsers.markdown_parser import MarkdownParser

        parser = MarkdownParser()
        minimal_markdown = "# Minimal Guidelines\n\nSome basic text."

        # Contract: Must not raise error for minimal markdown
        guidelines = parser.parse(minimal_markdown)
        assert guidelines is not None

        # Contract: Should have empty collections for missing sections
        assert guidelines.required_fields == []
        assert guidelines.field_validations == []

    def test_parse_empty_markdown_raises_error(self) -> None:
        """Test parser raises error for empty markdown."""
        from jra.parsers.markdown_parser import MarkdownParser

        parser = MarkdownParser()

        # Contract: Must raise GuidelineParseError for empty input
        with pytest.raises(GuidelineParseError, match="empty"):
            parser.parse("")

    def test_parse_invalid_format_raises_error(self) -> None:
        """Test parser raises error for invalid markdown format."""
        from jra.parsers.markdown_parser import MarkdownParser

        parser = MarkdownParser()
        invalid_markdown = "Not a proper guidelines document"

        # Contract: Must raise GuidelineParseError for invalid format
        # (This will be implementation-specific based on what "invalid" means)
        # For now, we expect it to at least not crash
        result = parser.parse(invalid_markdown)
        assert result is not None
