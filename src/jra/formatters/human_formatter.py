"""Human-readable formatter for evaluation reports.

Formats evaluation reports for terminal display with optional colors.
"""

from typing import Optional

from jra.models.report import EvaluationReport
from jra.models.violation import ViolationSeverity


class HumanFormatter:
    """Formatter for human-readable terminal output.

    Produces formatted text output suitable for terminal display.
    """

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

    def __init__(self, use_color: bool = True) -> None:
        """Initialize human formatter.

        Args:
            use_color: Whether to use ANSI color codes
        """
        self.use_color = use_color

    def format(self, report: EvaluationReport) -> str:
        """Format evaluation report for human reading.

        Args:
            report: Evaluation report to format

        Returns:
            Formatted string for terminal display
        """
        lines = []

        # Header
        lines.append(self._format_header(report))
        lines.append("")

        # Compliance status
        lines.append(self._format_compliance_status(report))
        lines.append("")

        # Compliance score
        lines.append(self._format_score(report))
        lines.append("")

        # Violations summary
        if report.compliance.total_violations > 0:
            lines.append(self._format_violations_summary(report))
            lines.append("")

            # Violation details
            lines.append(self._format_violations(report))
        else:
            lines.append(self._colorize("✓ No violations found!", self.GREEN))

        lines.append("")
        lines.append(self._format_footer(report))

        return "\n".join(lines)

    def _format_header(self, report: EvaluationReport) -> str:
        """Format report header."""
        header = f"{'=' * 70}\n"
        header += self._colorize(f"Evaluation Report: {report.ticket_key}", self.BOLD)
        header += f"\n{'=' * 70}"
        return header

    def _format_compliance_status(self, report: EvaluationReport) -> str:
        """Format compliance status."""
        if report.is_pass():
            status = self._colorize("✅ COMPLIANT", self.GREEN + self.BOLD)
        else:
            status = self._colorize("❌ NON-COMPLIANT", self.RED + self.BOLD)

        return f"Status: {status}"

    def _format_score(self, report: EvaluationReport) -> str:
        """Format compliance score."""
        score = report.get_score()
        grade = report.get_grade()

        # Color based on grade
        if grade == "A":
            color = self.GREEN
        elif grade == "B":
            color = self.CYAN
        elif grade == "C":
            color = self.YELLOW
        else:
            color = self.RED

        score_text = self._colorize(f"{score:.1f}%", color + self.BOLD)
        grade_text = self._colorize(f"Grade: {grade}", color)

        return f"Compliance Score: {score_text} ({grade_text})"

    def _format_violations_summary(self, report: EvaluationReport) -> str:
        """Format violations summary."""
        lines = [self._colorize("Violations Summary:", self.BOLD)]

        compliance = report.compliance

        if compliance.critical_violations > 0:
            lines.append(
                f"  {self._colorize('CRITICAL:', self.RED)} {compliance.critical_violations}"
            )

        if compliance.high_violations > 0:
            lines.append(
                f"  {self._colorize('HIGH:', self.RED)} {compliance.high_violations}"
            )

        if compliance.medium_violations > 0:
            lines.append(
                f"  {self._colorize('MEDIUM:', self.YELLOW)} {compliance.medium_violations}"
            )

        if compliance.low_violations > 0:
            lines.append(
                f"  {self._colorize('LOW:', self.BLUE)} {compliance.low_violations}"
            )

        lines.append(f"  {self._colorize('TOTAL:', self.BOLD)} {compliance.total_violations}")

        return "\n".join(lines)

    def _format_violations(self, report: EvaluationReport) -> str:
        """Format detailed violation list."""
        if not report.compliance.violations:
            return ""

        lines = [self._colorize("Violation Details:", self.BOLD)]
        lines.append("")

        for i, violation in enumerate(report.compliance.violations, 1):
            # Severity badge
            severity_color = self._get_severity_color(violation.severity)
            severity_badge = self._colorize(f"[{violation.severity.value}]", severity_color)

            # Field name
            field_text = self._colorize(violation.field, self.CYAN)

            # Violation line
            lines.append(f"{i}. {severity_badge} {field_text}")
            lines.append(f"   {violation.message}")

            if violation.reference:
                lines.append(f"   Reference: {violation.reference}")

            if violation.current_value:
                lines.append(f"   Current: {violation.current_value}")

            if violation.expected_value:
                lines.append(f"   Expected: {violation.expected_value}")

            if violation.suggestion:
                suggestion_text = self._colorize(f"💡 {violation.suggestion}", self.MAGENTA)
                lines.append(f"   {suggestion_text}")

            lines.append("")

        return "\n".join(lines)

    def _format_footer(self, report: EvaluationReport) -> str:
        """Format report footer."""
        timestamp = report.evaluated_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"Evaluated at: {timestamp}"

    def _get_severity_color(self, severity: ViolationSeverity) -> str:
        """Get color for severity level."""
        if not self.use_color:
            return ""

        severity_colors = {
            ViolationSeverity.CRITICAL: self.RED + self.BOLD,
            ViolationSeverity.HIGH: self.RED,
            ViolationSeverity.MEDIUM: self.YELLOW,
            ViolationSeverity.LOW: self.BLUE,
            ViolationSeverity.INFO: self.CYAN,
        }

        return severity_colors.get(severity, "")

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if color is enabled."""
        if not self.use_color or not color:
            return text

        return f"{color}{text}{self.RESET}"
