"""Pydantic models for process guidelines representation.

Models for parsing and validating process guidelines from markdown.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RequiredField(BaseModel):
    """Model for required field specification."""

    field_name: str = Field(..., description="Name of the required field")
    issue_type: Optional[str] = Field(
        None, description="Issue type this applies to (Story, Bug, etc.), None for all types"
    )
    description: Optional[str] = Field(None, description="Description of the requirement")

    class Config:
        """Pydantic configuration."""

        frozen = False


class FieldValidation(BaseModel):
    """Model for field validation rules."""

    field_name: str = Field(..., description="Name of the field to validate")
    rules: List[str] = Field(default_factory=list, description="Validation rules")
    min_length: Optional[int] = Field(None, description="Minimum length requirement")
    max_length: Optional[int] = Field(None, description="Maximum length requirement")
    pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    required_sections: List[str] = Field(
        default_factory=list, description="Required sections in field content"
    )
    examples: List[str] = Field(default_factory=list, description="Example values")

    class Config:
        """Pydantic configuration."""

        frozen = False


class WorkflowRule(BaseModel):
    """Model for workflow transition rules."""

    from_status: str = Field(..., description="Source status")
    to_status: str = Field(..., description="Target status")
    required_fields: List[str] = Field(
        default_factory=list, description="Fields required for this transition"
    )
    required_conditions: List[str] = Field(
        default_factory=list, description="Conditions that must be met"
    )
    description: Optional[str] = Field(None, description="Rule description")

    class Config:
        """Pydantic configuration."""

        frozen = False


class QualityStandard(BaseModel):
    """Model for quality standards and definitions."""

    name: str = Field(..., description="Standard name (e.g., 'Definition of Ready')")
    criteria: List[str] = Field(default_factory=list, description="Quality criteria")
    description: Optional[str] = Field(None, description="Standard description")

    class Config:
        """Pydantic configuration."""

        frozen = False


class CustomRule(BaseModel):
    """Model for custom validation rules."""

    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    applies_to: List[str] = Field(
        default_factory=list, description="Issue types this rule applies to"
    )
    conditions: List[str] = Field(default_factory=list, description="Rule conditions")
    severity: str = Field(default="MEDIUM", description="Violation severity if rule is broken")

    class Config:
        """Pydantic configuration."""

        frozen = False


class ProcessGuidelines(BaseModel):
    """Complete process guidelines model.

    Represents team process guidelines parsed from markdown documentation.
    """

    # Metadata
    version: Optional[str] = Field(None, description="Guidelines version")
    last_updated: Optional[str] = Field(None, description="Last update date")
    team: Optional[str] = Field(None, description="Team name")

    # Core requirements
    required_fields: List[RequiredField] = Field(
        default_factory=list, description="Required fields specification"
    )
    field_validations: List[FieldValidation] = Field(
        default_factory=list, description="Field validation rules"
    )
    workflow_rules: List[WorkflowRule] = Field(
        default_factory=list, description="Workflow transition rules"
    )

    # Quality standards
    quality_standards: List[QualityStandard] = Field(
        default_factory=list, description="Quality standards (DoR, DoD, etc.)"
    )

    # Custom rules (for extensibility)
    custom_rules: List[CustomRule] = Field(
        default_factory=list, description="Custom validation rules"
    )

    # Metadata fields
    raw_content: Optional[str] = Field(None, description="Original markdown content")
    sections: Dict[str, str] = Field(
        default_factory=dict, description="Extracted sections from markdown"
    )

    class Config:
        """Pydantic configuration."""

        frozen = False
        validate_assignment = True

    def get_required_fields_for_type(self, issue_type: str) -> List[RequiredField]:
        """Get required fields for a specific issue type.

        Args:
            issue_type: Issue type name (Story, Bug, Task, Epic)

        Returns:
            List of required fields applicable to this issue type
        """
        return [
            field
            for field in self.required_fields
            if field.issue_type is None or field.issue_type == issue_type
        ]

    def get_validation_for_field(self, field_name: str) -> Optional[FieldValidation]:
        """Get validation rules for a specific field.

        Args:
            field_name: Field name to look up

        Returns:
            FieldValidation object if found, None otherwise
        """
        for validation in self.field_validations:
            if validation.field_name.lower() == field_name.lower():
                return validation
        return None

    def get_workflow_transitions_from(self, status: str) -> List[WorkflowRule]:
        """Get valid workflow transitions from a given status.

        Args:
            status: Current status name

        Returns:
            List of valid transitions from this status
        """
        return [rule for rule in self.workflow_rules if rule.from_status == status]

    def get_workflow_rule(self, from_status: str, to_status: str) -> Optional[WorkflowRule]:
        """Get workflow rule for a specific transition.

        Args:
            from_status: Source status
            to_status: Target status

        Returns:
            WorkflowRule if found, None otherwise
        """
        for rule in self.workflow_rules:
            if rule.from_status == from_status and rule.to_status == to_status:
                return rule
        return None

    def get_quality_standard(self, name: str) -> Optional[QualityStandard]:
        """Get quality standard by name.

        Args:
            name: Standard name (e.g., "Definition of Ready")

        Returns:
            QualityStandard if found, None otherwise
        """
        for standard in self.quality_standards:
            if standard.name.lower() == name.lower():
                return standard
        return None

    def get_custom_rules_for_type(self, issue_type: str) -> List[CustomRule]:
        """Get custom rules applicable to an issue type.

        Args:
            issue_type: Issue type name

        Returns:
            List of applicable custom rules
        """
        return [
            rule
            for rule in self.custom_rules
            if not rule.applies_to or issue_type in rule.applies_to
        ]

    def has_section(self, section_name: str) -> bool:
        """Check if guidelines contain a specific section.

        Args:
            section_name: Section name to check

        Returns:
            True if section exists
        """
        return section_name in self.sections

    def get_section(self, section_name: str, default: str = "") -> str:
        """Get content of a specific section.

        Args:
            section_name: Section name
            default: Default value if section doesn't exist

        Returns:
            Section content or default
        """
        return self.sections.get(section_name, default)
