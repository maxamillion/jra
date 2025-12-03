"""JSON formatter for evaluation reports.

Formats evaluation reports as JSON output.
"""

import json
from typing import Optional

from jra.models.report import EvaluationReport


class JSONFormatter:
    """Formatter for JSON output.

    Produces machine-readable JSON evaluation reports.
    """

    def __init__(self, indent: Optional[int] = 2) -> None:
        """Initialize JSON formatter.

        Args:
            indent: Number of spaces for indentation (None for compact)
        """
        self.indent = indent

    def format(self, report: EvaluationReport) -> str:
        """Format evaluation report as JSON.

        Args:
            report: Evaluation report to format

        Returns:
            JSON string representation
        """
        # Convert report to dictionary
        data = report.to_dict()

        # Serialize to JSON
        json_output = json.dumps(data, indent=self.indent, ensure_ascii=False)

        return json_output
