"""JSON schema validation for input and output contracts.

Validates JSON data against defined schemas for Jira inputs and evaluation outputs.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from jra.utils.exceptions import ValidationError


class SchemaValidator:
    """Validator for JSON schemas.

    Validates input and output JSON against contract schemas.
    """

    def __init__(self, schema_dir: Optional[Path] = None) -> None:
        """Initialize schema validator.

        Args:
            schema_dir: Directory containing schema files (defaults to contracts/)
        """
        if schema_dir is None:
            # Default to contracts directory in specs
            self.schema_dir = (
                Path(__file__).parents[3] / "specs" / "001-jira-evaluation" / "contracts"
            )
        else:
            self.schema_dir = schema_dir

        self._schemas: Dict[str, Dict[str, Any]] = {}

    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load a JSON schema by name.

        Args:
            schema_name: Name of schema file (without .json extension)

        Returns:
            Loaded schema dictionary

        Raises:
            ValidationError: If schema file not found or invalid
        """
        if schema_name in self._schemas:
            return self._schemas[schema_name]

        schema_path = self.schema_dir / f"{schema_name}.json"

        if not schema_path.exists():
            raise ValidationError(
                f"Schema file not found: {schema_path}",
                context={"schema_name": schema_name, "path": str(schema_path)},
            )

        try:
            with open(schema_path) as f:
                schema = json.load(f)

            self._schemas[schema_name] = schema
            return schema

        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON in schema file: {schema_name}",
                context={"error": str(e)},
            ) from e
        except Exception as e:
            raise ValidationError(
                f"Failed to load schema: {schema_name}",
                context={"error": str(e)},
            ) from e

    def validate_jira_input(self, data: Dict[str, Any]) -> bool:
        """Validate Jira JSON input against schema.

        Args:
            data: Jira JSON data to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = self.load_schema("input-schema")
            self._validate_against_schema(data, schema, "Jira input")
            return True
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError("Jira input validation failed", context={"error": str(e)}) from e

    def validate_evaluation_output(self, data: Dict[str, Any]) -> bool:
        """Validate evaluation report output against schema.

        Args:
            data: Evaluation report JSON to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        try:
            schema = self.load_schema("output-schema")
            self._validate_against_schema(data, schema, "Evaluation output")
            return True
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                "Evaluation output validation failed", context={"error": str(e)}
            ) from e

    def _validate_against_schema(
        self, data: Dict[str, Any], schema: Dict[str, Any], data_type: str
    ) -> None:
        """Validate data against a JSON schema.

        Args:
            data: Data to validate
            schema: JSON schema
            data_type: Human-readable description of data type

        Raises:
            ValidationError: If validation fails
        """
        # Basic type validation
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "object" and not isinstance(data, dict):
                raise ValidationError(
                    f"{data_type} must be an object",
                    context={"expected_type": "object", "actual_type": type(data).__name__},
                )

        # Required fields validation
        if "required" in schema and isinstance(data, dict):
            required_fields = schema["required"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                raise ValidationError(
                    f"{data_type} missing required fields",
                    context={"missing_fields": missing_fields},
                )

        # Properties validation
        if "properties" in schema and isinstance(data, dict):
            for field_name, field_schema in schema["properties"].items():
                if field_name in data:
                    field_value = data[field_name]

                    # Type validation for field
                    if "type" in field_schema:
                        field_type = field_schema["type"]
                        if not self._check_type(field_value, field_type):
                            raise ValidationError(
                                f"{data_type} field '{field_name}' has wrong type",
                                context={
                                    "field": field_name,
                                    "expected_type": field_type,
                                    "actual_type": type(field_value).__name__,
                                },
                            )

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON schema type.

        Args:
            value: Value to check
            expected_type: Expected type from schema

        Returns:
            True if type matches
        """
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }

        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip validation

        return isinstance(value, expected_python_type)
