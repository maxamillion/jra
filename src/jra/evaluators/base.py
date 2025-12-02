"""Base evaluator interface.

Abstract base class for all evaluators.
"""

from abc import ABC, abstractmethod

from jra.models.guidelines import ProcessGuidelines
from jra.models.jira import JiraIssue
from jra.models.report import EvaluationReport


class BaseEvaluator(ABC):
    """Abstract base class for evaluators.

    All evaluators must implement the evaluate method.
    """

    @abstractmethod
    def evaluate(self, issue: JiraIssue, guidelines: ProcessGuidelines) -> EvaluationReport:
        """Evaluate a Jira issue against process guidelines.

        Args:
            issue: Jira issue to evaluate
            guidelines: Process guidelines to evaluate against

        Returns:
            Evaluation report with results

        Raises:
            EvaluationError: If evaluation fails
        """
        pass
