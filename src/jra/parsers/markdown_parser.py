"""Markdown parser for process guidelines.

Parses markdown documents containing team process guidelines into structured models.
"""

import re
from typing import Dict, List, Optional

from jra.models.guidelines import (
    FieldValidation,
    ProcessGuidelines,
    QualityStandard,
    RequiredField,
    WorkflowRule,
)
from jra.utils.exceptions import GuidelineParseError


class MarkdownParser:
    """Parser for process guidelines in markdown format.

    Extracts structured rules and requirements from markdown documentation.
    """

    def parse(self, content: str) -> ProcessGuidelines:
        """Parse markdown content into ProcessGuidelines model.

        Args:
            content: Markdown text content

        Returns:
            Parsed ProcessGuidelines instance

        Raises:
            GuidelineParseError: If markdown is empty or invalid
        """
        if not content or not content.strip():
            raise GuidelineParseError("Cannot parse empty markdown content")

        try:
            # Extract metadata
            version = self._extract_version(content)
            last_updated = self._extract_last_updated(content)
            team = self._extract_team(content)

            # Extract sections
            sections = self._extract_sections(content)

            # Parse required fields
            required_fields = self._parse_required_fields(sections, content)

            # Parse field validations
            field_validations = self._parse_field_validations(sections, content)

            # Parse workflow rules
            workflow_rules = self._parse_workflow_rules(sections, content)

            # Parse quality standards
            quality_standards = self._parse_quality_standards(sections, content)

            return ProcessGuidelines(
                version=version,
                last_updated=last_updated,
                team=team,
                required_fields=required_fields,
                field_validations=field_validations,
                workflow_rules=workflow_rules,
                quality_standards=quality_standards,
                raw_content=content,
                sections=sections,
            )

        except GuidelineParseError:
            raise
        except Exception as e:
            raise GuidelineParseError(f"Failed to parse markdown: {str(e)}") from e

    def _extract_version(self, content: str) -> Optional[str]:
        """Extract version from markdown."""
        match = re.search(r"Version:\s*(\S+)", content, re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_last_updated(self, content: str) -> Optional[str]:
        """Extract last updated date from markdown."""
        match = re.search(r"Last Updated:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_team(self, content: str) -> Optional[str]:
        """Extract team name from markdown."""
        match = re.search(r"Team:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract named sections from markdown.

        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}

        # Find all headers (## or #) and their content
        header_pattern = r"^#+\s+(.+?)$"
        lines = content.split("\n")

        current_section = None
        current_content: list[str] = []

        for line in lines:
            header_match = re.match(header_pattern, line)
            if header_match:
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = header_match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _parse_required_fields(self, sections: Dict[str, str], content: str) -> List[RequiredField]:
        """Parse required fields from markdown."""
        required_fields: list[RequiredField] = []

        # Look for "Required Fields" section
        required_section = None
        for section_name, section_content in sections.items():
            if "required" in section_name.lower() and "field" in section_name.lower():
                required_section = section_content
                break

        if not required_section:
            return required_fields

        # Parse universal required fields
        universal_match = re.search(
            r"Universal Required Fields.*?:(.*?)(?=###|##|$)",
            required_section,
            re.DOTALL | re.IGNORECASE,
        )
        if universal_match:
            field_text = universal_match.group(1)
            fields = self._extract_field_list(field_text)
            for field in fields:
                required_fields.append(
                    RequiredField(field_name=field, issue_type=None, description=None)
                )

        # Parse story-specific required fields
        story_match = re.search(
            r"Story-Specific Required Fields.*?:(.*?)(?=###|##|$)",
            required_section,
            re.DOTALL | re.IGNORECASE,
        )
        if story_match:
            field_text = story_match.group(1)
            fields = self._extract_field_list(field_text)
            for field in fields:
                required_fields.append(
                    RequiredField(field_name=field, issue_type="Story", description=None)
                )

        # Parse bug-specific required fields
        bug_match = re.search(
            r"Bug-Specific Required Fields.*?:(.*?)(?=###|##|$)",
            required_section,
            re.DOTALL | re.IGNORECASE,
        )
        if bug_match:
            field_text = bug_match.group(1)
            fields = self._extract_field_list(field_text)
            for field in fields:
                required_fields.append(
                    RequiredField(field_name=field, issue_type="Bug", description=None)
                )

        # Parse epic-specific required fields
        epic_match = re.search(
            r"Epic-Specific Required Fields.*?:(.*?)(?=###|##|$)",
            required_section,
            re.DOTALL | re.IGNORECASE,
        )
        if epic_match:
            field_text = epic_match.group(1)
            fields = self._extract_field_list(field_text)
            for field in fields:
                required_fields.append(
                    RequiredField(field_name=field, issue_type="Epic", description=None)
                )

        return required_fields

    def _parse_field_validations(
        self, sections: Dict[str, str], content: str
    ) -> List[FieldValidation]:
        """Parse field validation rules from markdown."""
        validations: list[FieldValidation] = []

        # Look for "Field Validations" section
        validation_section = None
        for section_name, section_content in sections.items():
            if "field validation" in section_name.lower() or "validation" in section_name.lower():
                validation_section = section_content
                break

        if not validation_section:
            return validations

        # Parse summary validation
        summary_match = re.search(
            r"Summary Validation(.*?)(?=###|##|$)", validation_section, re.DOTALL | re.IGNORECASE
        )
        if summary_match:
            validation_text = summary_match.group(1)
            validation = self._parse_single_field_validation("summary", validation_text)
            if validation:
                validations.append(validation)

        # Parse description validation
        desc_match = re.search(
            r"Description Validation(.*?)(?=###|##|$)",
            validation_section,
            re.DOTALL | re.IGNORECASE,
        )
        if desc_match:
            validation_text = desc_match.group(1)
            validation = self._parse_single_field_validation("description", validation_text)
            if validation:
                validations.append(validation)

        # Parse priority validation
        priority_match = re.search(
            r"Priority Validation(.*?)(?=###|##|$)", validation_section, re.DOTALL | re.IGNORECASE
        )
        if priority_match:
            validation_text = priority_match.group(1)
            validation = self._parse_single_field_validation("priority", validation_text)
            if validation:
                validations.append(validation)

        return validations

    def _parse_single_field_validation(
        self, field_name: str, validation_text: str
    ) -> Optional[FieldValidation]:
        """Parse validation rules for a single field."""
        rules = []
        min_length = None
        max_length = None
        required_sections = []

        # Extract length requirements
        length_match = re.search(r"Length:\s*(\d+)-(\d+)\s*characters", validation_text)
        if length_match:
            min_length = int(length_match.group(1))
            max_length = int(length_match.group(2))
            rules.append(f"Length must be {min_length}-{max_length} characters")

        # Minimum length only
        min_match = re.search(r"Minimum length:\s*(\d+)", validation_text, re.IGNORECASE)
        if min_match and not length_match:
            min_length = int(min_match.group(1))
            rules.append(f"Minimum length: {min_length} characters")

        # Extract required sections
        sections_match = re.search(
            r"Required Sections.*?:(.*?)(?=\*\*|##|$)", validation_text, re.DOTALL | re.IGNORECASE
        )
        if sections_match:
            sections_text = sections_match.group(1)
            # Look for markdown code blocks or bullet lists
            for line in sections_text.split("\n"):
                if line.strip().startswith("-") or line.strip().startswith("##"):
                    section = line.strip().lstrip("-").lstrip("#").strip()
                    if section:
                        required_sections.append(section)

        # Extract general rules from "Requirements:" section
        req_match = re.search(
            r"\*\*Requirements\*\*:(.*?)(?=\*\*|##|$)", validation_text, re.DOTALL
        )
        if req_match:
            req_text = req_match.group(1)
            for line in req_text.split("\n"):
                line = line.strip()
                if line.startswith("-"):
                    rule = line.lstrip("-").strip()
                    if rule and rule not in rules:
                        rules.append(rule)

        if rules or min_length or max_length or required_sections:
            return FieldValidation(
                field_name=field_name,
                rules=rules,
                min_length=min_length,
                max_length=max_length,
                pattern=None,
                required_sections=required_sections,
            )

        return None

    def _parse_workflow_rules(self, sections: Dict[str, str], content: str) -> List[WorkflowRule]:
        """Parse workflow transition rules from markdown."""
        rules: list[WorkflowRule] = []

        # Look for "Workflow Rules" section
        workflow_section = None
        for section_name, section_content in sections.items():
            if "workflow" in section_name.lower():
                workflow_section = section_content
                break

        if not workflow_section:
            return rules

        # Parse required transitions section
        transitions_match = re.search(
            r"Required Transitions(.*?)(?=###|##|$)", workflow_section, re.DOTALL | re.IGNORECASE
        )
        if transitions_match:
            transitions_text = transitions_match.group(1)

            # Look for numbered transition rules
            transition_pattern = r"\d+\.\s*\*\*(.+?)\s*→\s*(.+?)\*\*:(.*?)(?=\d+\.|$)"
            matches = re.finditer(transition_pattern, transitions_text, re.DOTALL)

            for match in matches:
                from_status = match.group(1).strip()
                to_status = match.group(2).strip()
                requirements_text = match.group(3)

                required_fields = []
                required_conditions = []

                # Extract "Must have:" items
                for line in requirements_text.split("\n"):
                    line = line.strip()
                    if line.startswith("-") and "Must have:" in line:
                        field = line.split("Must have:")[-1].strip()
                        required_fields.append(field)
                    elif line.startswith("-") and "must" in line.lower():
                        required_conditions.append(line.lstrip("-").strip())

                rules.append(
                    WorkflowRule(
                        from_status=from_status,
                        to_status=to_status,
                        required_fields=required_fields,
                        required_conditions=required_conditions,
                        description=None,
                    )
                )

        return rules

    def _parse_quality_standards(
        self, sections: Dict[str, str], content: str
    ) -> List[QualityStandard]:
        """Parse quality standards (DoR, DoD, etc.) from markdown."""
        standards = []

        # Look for "Definition of Ready" section
        dor_section = None
        for section_name, section_content in sections.items():
            if "definition of ready" in section_name.lower():
                dor_section = section_content
                break

        if dor_section:
            criteria = self._extract_checklist(dor_section)
            if criteria:
                standards.append(
                    QualityStandard(
                        name="Definition of Ready",
                        criteria=criteria,
                        description="Sprint planning readiness",
                    )
                )

        # Look for "Definition of Done" section
        dod_section = None
        for section_name, section_content in sections.items():
            if "definition of done" in section_name.lower():
                dod_section = section_content
                break

        if dod_section:
            criteria = self._extract_checklist(dod_section)
            if criteria:
                standards.append(
                    QualityStandard(
                        name="Definition of Done",
                        criteria=criteria,
                        description="Completion criteria",
                    )
                )

        return standards

    def _extract_field_list(self, text: str) -> List[str]:
        """Extract field names from bullet list or similar text."""
        fields = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                # Extract field name (first bold text or first word)
                field_match = re.search(r"\*\*(.+?)\*\*", line)
                if field_match:
                    field = field_match.group(1).split(":")[0].strip()
                    fields.append(field)

        return fields

    def _extract_checklist(self, text: str) -> List[str]:
        """Extract checklist items from text."""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("- [ ]") or line.startswith("- [x]") or line.startswith("- [X]"):
                item = line.replace("- [ ]", "").replace("- [x]", "").replace("- [X]", "").strip()
                if item:
                    items.append(item)

        return items
