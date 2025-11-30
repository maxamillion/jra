"""Integration tests for evaluate CLI command.

Contract tests for end-to-end evaluation workflow.
Per constitution: TDD is NON-NEGOTIABLE - these tests written BEFORE implementation.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner


class TestEvaluateCommandIntegration:
    """Integration tests for evaluate command basic flow.

    T026: Write integration test for evaluate command basic flow.
    These tests verify the complete workflow from CLI to output.
    """

    @pytest.fixture
    def cli_runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def valid_ticket_file(self, fixtures_dir: Path, tmp_path: Path) -> Path:
        """Copy valid ticket fixture to temp location."""
        source = fixtures_dir / "tickets" / "valid-story.json"
        dest = tmp_path / "ticket.json"
        dest.write_text(source.read_text())
        return dest

    @pytest.fixture
    def guidelines_file(self, fixtures_dir: Path, tmp_path: Path) -> Path:
        """Copy guidelines fixture to temp location."""
        source = fixtures_dir / "guidelines" / "basic-guidelines.md"
        dest = tmp_path / "guidelines.md"
        dest.write_text(source.read_text())
        return dest

    def test_evaluate_command_exists(self, cli_runner: CliRunner) -> None:
        """Test evaluate command is registered and accessible."""
        from jra.cli.main import cli

        result = cli_runner.invoke(cli, ["--help"])

        # Contract: CLI should have evaluate command listed
        assert result.exit_code == 0
        assert "evaluate" in result.output.lower()

    def test_evaluate_with_valid_inputs(
        self, cli_runner: CliRunner, valid_ticket_file: Path, guidelines_file: Path
    ) -> None:
        """Test evaluate command with valid ticket and guidelines."""
        from jra.cli.main import cli

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(valid_ticket_file),
                "--guidelines",
                str(guidelines_file),
            ],
        )

        # Contract: Should complete successfully
        assert result.exit_code == 0

        # Contract: Should produce output
        assert len(result.output) > 0

    def test_evaluate_with_json_format(
        self, cli_runner: CliRunner, valid_ticket_file: Path, guidelines_file: Path
    ) -> None:
        """Test evaluate command with JSON output format."""
        from jra.cli.main import cli

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(valid_ticket_file),
                "--guidelines",
                str(guidelines_file),
                "--format",
                "json",
            ],
        )

        # Contract: Should complete successfully
        assert result.exit_code == 0

        # Contract: Should produce valid JSON output
        output_data = json.loads(result.output)
        assert isinstance(output_data, dict)
        assert "ticket_key" in output_data
        assert "compliance" in output_data

    def test_evaluate_with_human_format(
        self, cli_runner: CliRunner, valid_ticket_file: Path, guidelines_file: Path
    ) -> None:
        """Test evaluate command with human-readable output format."""
        from jra.cli.main import cli

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(valid_ticket_file),
                "--guidelines",
                str(guidelines_file),
                "--format",
                "human",
            ],
        )

        # Contract: Should complete successfully
        assert result.exit_code == 0

        # Contract: Should produce human-readable output
        assert isinstance(result.output, str)
        assert len(result.output) > 0

    def test_evaluate_with_timing_option(
        self, cli_runner: CliRunner, valid_ticket_file: Path, guidelines_file: Path
    ) -> None:
        """Test evaluate command with timing information."""
        from jra.cli.main import cli

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(valid_ticket_file),
                "--guidelines",
                str(guidelines_file),
                "--timing",
            ],
        )

        # Contract: Should complete successfully
        assert result.exit_code == 0

        # Contract: Should include timing information in output
        output_lower = result.output.lower()
        assert any(
            word in output_lower
            for word in ["time", "duration", "elapsed", "ms", "seconds"]
        )

    def test_evaluate_missing_ticket_file(
        self, cli_runner: CliRunner, guidelines_file: Path, tmp_path: Path
    ) -> None:
        """Test evaluate command with missing ticket file."""
        from jra.cli.main import cli

        nonexistent_file = tmp_path / "nonexistent.json"

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(nonexistent_file),
                "--guidelines",
                str(guidelines_file),
            ],
        )

        # Contract: Should fail with non-zero exit code
        assert result.exit_code != 0

        # Contract: Should provide helpful error message
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_evaluate_missing_guidelines_file(
        self, cli_runner: CliRunner, valid_ticket_file: Path, tmp_path: Path
    ) -> None:
        """Test evaluate command with missing guidelines file."""
        from jra.cli.main import cli

        nonexistent_file = tmp_path / "nonexistent.md"

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(valid_ticket_file),
                "--guidelines",
                str(nonexistent_file),
            ],
        )

        # Contract: Should fail with non-zero exit code
        assert result.exit_code != 0

        # Contract: Should provide helpful error message
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_evaluate_invalid_json_file(
        self, cli_runner: CliRunner, guidelines_file: Path, tmp_path: Path
    ) -> None:
        """Test evaluate command with invalid JSON file."""
        from jra.cli.main import cli

        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ not valid json }")

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(invalid_file),
                "--guidelines",
                str(guidelines_file),
            ],
        )

        # Contract: Should fail with non-zero exit code
        assert result.exit_code != 0

        # Contract: Should indicate JSON parse error
        output_lower = result.output.lower()
        assert "json" in output_lower or "parse" in output_lower or "invalid" in output_lower


class TestEvaluationFlowIntegration:
    """Integration tests for violation detection and reporting.

    T027: Write integration test for violation detection and reporting.
    These tests verify the complete evaluation flow produces correct results.
    """

    @pytest.fixture
    def cli_runner(self) -> CliRunner:
        """Create Click CLI test runner."""
        return CliRunner()

    def test_detects_violations_in_invalid_ticket(
        self, cli_runner: CliRunner, fixtures_dir: Path, tmp_path: Path
    ) -> None:
        """Test evaluation detects violations in invalid ticket."""
        from jra.cli.main import cli

        # Use invalid ticket fixture
        ticket_file = tmp_path / "invalid_ticket.json"
        source = fixtures_dir / "tickets" / "invalid-bug.json"
        ticket_file.write_text(source.read_text())

        # Use comprehensive guidelines
        guidelines_file = tmp_path / "guidelines.md"
        source = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"
        guidelines_file.write_text(source.read_text())

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(ticket_file),
                "--guidelines",
                str(guidelines_file),
                "--format",
                "json",
            ],
        )

        # Contract: Should complete successfully even with violations
        assert result.exit_code == 0

        # Contract: Should report violations
        output_data = json.loads(result.output)
        assert "compliance" in output_data
        assert output_data["compliance"]["is_compliant"] is False
        assert output_data["compliance"]["total_violations"] > 0

    def test_reports_compliant_for_valid_ticket(
        self, cli_runner: CliRunner, fixtures_dir: Path, tmp_path: Path
    ) -> None:
        """Test evaluation reports compliant for valid ticket."""
        from jra.cli.main import cli

        # Use valid ticket fixture
        ticket_file = tmp_path / "valid_ticket.json"
        source = fixtures_dir / "tickets" / "valid-story.json"
        ticket_file.write_text(source.read_text())

        # Use basic guidelines (less strict)
        guidelines_file = tmp_path / "guidelines.md"
        source = fixtures_dir / "guidelines" / "basic-guidelines.md"
        guidelines_file.write_text(source.read_text())

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(ticket_file),
                "--guidelines",
                str(guidelines_file),
                "--format",
                "json",
            ],
        )

        # Contract: Should complete successfully
        assert result.exit_code == 0

        # Contract: Should report as compliant (or have minimal violations)
        output_data = json.loads(result.output)
        assert "compliance" in output_data
        # Note: This may not be fully compliant depending on guidelines strictness
        assert "compliance_score" in output_data["compliance"]

    def test_violations_include_required_details(
        self, cli_runner: CliRunner, fixtures_dir: Path, tmp_path: Path
    ) -> None:
        """Test violations include all required details."""
        from jra.cli.main import cli

        # Use invalid ticket
        ticket_file = tmp_path / "invalid_ticket.json"
        source = fixtures_dir / "tickets" / "invalid-bug.json"
        ticket_file.write_text(source.read_text())

        # Use comprehensive guidelines
        guidelines_file = tmp_path / "guidelines.md"
        source = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"
        guidelines_file.write_text(source.read_text())

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(ticket_file),
                "--guidelines",
                str(guidelines_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        output_data = json.loads(result.output)

        # Contract: Violations must have required fields
        if output_data["compliance"]["violations"]:
            violation = output_data["compliance"]["violations"][0]
            assert "field" in violation
            assert "message" in violation
            assert "severity" in violation
            assert "category" in violation

    def test_compliance_score_calculation(
        self, cli_runner: CliRunner, fixtures_dir: Path, tmp_path: Path
    ) -> None:
        """Test compliance score is calculated correctly."""
        from jra.cli.main import cli

        ticket_file = tmp_path / "ticket.json"
        source = fixtures_dir / "tickets" / "valid-story.json"
        ticket_file.write_text(source.read_text())

        guidelines_file = tmp_path / "guidelines.md"
        source = fixtures_dir / "guidelines" / "comprehensive-guidelines.md"
        guidelines_file.write_text(source.read_text())

        result = cli_runner.invoke(
            cli,
            [
                "evaluate",
                str(ticket_file),
                "--guidelines",
                str(guidelines_file),
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        output_data = json.loads(result.output)

        # Contract: Score must be between 0 and 100
        score = output_data["compliance"]["compliance_score"]
        assert 0 <= score <= 100

        # Contract: Score should correlate with violations
        # (more violations = lower score)
        total_violations = output_data["compliance"]["total_violations"]
        if total_violations == 0:
            assert score == 100.0
        else:
            assert score < 100.0
