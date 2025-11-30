"""Custom exception hierarchy for JRA."""


class JRAException(Exception):
    """Base exception for all JRA errors."""

    def __init__(self, message: str, context: dict | None = None) -> None:
        """Initialize JRA exception.
        
        Args:
            message: Error message
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}


class ParseError(JRAException):
    """Base exception for parsing errors."""

    pass


class JiraParseError(ParseError):
    """Error parsing Jira JSON input."""

    pass


class GuidelineParseError(ParseError):
    """Error parsing process guidelines markdown."""

    pass


class ValidationError(JRAException):
    """Base exception for validation errors."""

    pass


class SchemaValidationError(ValidationError):
    """JSON schema validation error."""

    pass


class ConfigValidationError(ValidationError):
    """Configuration validation error."""

    pass


class EvaluationError(JRAException):
    """Base exception for evaluation errors."""

    pass


class ComplianceCheckError(EvaluationError):
    """Error during compliance checking."""

    pass


class QualityAssessmentError(EvaluationError):
    """Error during quality assessment."""

    pass


class OutputError(JRAException):
    """Base exception for output formatting errors."""

    pass


class FormattingError(OutputError):
    """Error formatting output."""

    pass


class IOError(OutputError):
    """Error with file I/O operations."""

    pass
