# Data Model: Jira Issue Evaluation AI Agent

**Phase**: 1 - Design & Contracts
**Date**: 2025-11-26
**Purpose**: Define core entities, validation rules, and relationships

## Entity Definitions

### 1. JiraIssue

**Purpose**: Represents a Jira ticket to be evaluated

**Fields**:
- `id`: Unique identifier (string, e.g., "12345")
- `key`: Human-readable key (string, e.g., "PROJ-123")
- `issue_type`: Type of issue (string: "Story", "Bug", "Epic", "Task", etc.)
- `status`: Current workflow status (string, e.g., "To Do", "In Progress", "Done")
- `summary`: Short title/description (string, max 255 chars typical)
- `description`: Detailed description (string, can be ADF/markdown/wiki)
- `description_format`: Format identifier (string: "adf", "markdown", "wiki", "text")
- `priority`: Priority level (optional string, e.g., "High", "Medium", "Low")
- `labels`: Tags/categories (list of strings)
- `components`: Project components (list of strings)
- `assignee`: Assigned user (optional User object)
- `reporter`: Ticket creator (User object)
- `created`: Creation timestamp (datetime)
- `updated`: Last update timestamp (datetime)
- `custom_fields`: Organization-specific fields (dict[str, Any])
- `comments`: List of comments (optional, list of Comment objects)
- `attachments`: List of attachments (optional, list of Attachment objects)

**Validation Rules**:
- `key` must match pattern `[A-Z]+-\d+`
- `issue_type` must be non-empty
- `status` must be non-empty
- `summary` must be 10-255 characters
- `description` should be non-empty (warning if missing)
- `created` must be before `updated`

**Relationships**:
- Has one `assignee` (User, optional)
- Has one `reporter` (User, required)
- Has many `comments` (Comment, optional)
- Has many `attachments` (Attachment, optional)

### 2. User

**Purpose**: Represents a Jira user (assignee, reporter)

**Fields**:
- `account_id`: Unique identifier (string)
- `display_name`: User's display name (string)
- `email`: Email address (optional string)
- `active`: Account status (boolean)

**Validation Rules**:
- `account_id` must be non-empty
- `display_name` must be non-empty
- `email` must be valid email format if present

### 3. Comment

**Purpose**: Represents a comment on a Jira ticket

**Fields**:
- `id`: Unique identifier (string)
- `author`: Comment author (User object)
- `body`: Comment text (string)
- `created`: Creation timestamp (datetime)
- `updated`: Last update timestamp (datetime)

**Validation Rules**:
- `body` must be non-empty
- `created` must be before or equal to `updated`

### 4. Attachment

**Purpose**: Represents a file attachment on a Jira ticket

**Fields**:
- `id`: Unique identifier (string)
- `filename`: File name (string)
- `mime_type`: MIME type (string, e.g., "image/png")
- `size`: File size in bytes (integer)
- `created`: Upload timestamp (datetime)

**Validation Rules**:
- `filename` must be non-empty
- `size` must be positive integer

### 5. ProcessGuidelines

**Purpose**: Represents team's process guidelines and requirements

**Fields**:
- `version`: Guideline version (string, e.g., "1.2.0")
- `last_updated`: Last modification date (datetime)
- `applies_to`: Issue types these guidelines apply to (list of strings)
- `required_fields`: Required field definitions (list of RequiredField)
- `field_validations`: Field validation rules (list of FieldValidation)
- `workflow_rules`: State transition rules (list of WorkflowRule)
- `quality_criteria`: Quality scoring rubrics (QualityCriteria object)
- `templates`: Example templates (dict[str, str])
- `metadata`: Additional guideline metadata (dict[str, Any])

**Validation Rules**:
- `version` must follow semantic versioning (X.Y.Z)
- `last_updated` must be valid datetime
- `applies_to` must contain at least one issue type
- `required_fields` must not be empty
- `quality_criteria` must be present

**Relationships**:
- Has many `required_fields` (RequiredField)
- Has many `field_validations` (FieldValidation)
- Has many `workflow_rules` (WorkflowRule)
- Has one `quality_criteria` (QualityCriteria)

### 6. RequiredField

**Purpose**: Defines a required field for specific issue types

**Fields**:
- `field_name`: Name of the field (string, e.g., "description", "acceptance_criteria")
- `issue_types`: Issue types this applies to (list of strings, e.g., ["Story", "Bug"])
- `required`: Whether field is mandatory (boolean)
- `description`: Human-readable description (string)
- `example`: Example of valid value (optional string)

**Validation Rules**:
- `field_name` must be non-empty
- `issue_types` must not be empty
- `description` must be non-empty

### 7. FieldValidation

**Purpose**: Defines validation rules for field content

**Fields**:
- `field_name`: Field to validate (string)
- `issue_types`: Applicable issue types (list of strings)
- `validation_type`: Type of validation (string: "length", "format", "vocabulary", "regex")
- `parameters`: Validation parameters (dict[str, Any])
- `error_message`: Message shown on violation (string)

**Validation Rules**:
- `field_name` must be non-empty
- `validation_type` must be one of supported types
- `parameters` must contain required keys for validation_type
- `error_message` must be non-empty

**Validation Type Parameters**:
- `length`: `{min: int, max: int}`
- `format`: `{pattern: str}` (regex pattern)
- `vocabulary`: `{allowed_values: list[str]}`
- `regex`: `{pattern: str, flags: list[str]}`

### 8. WorkflowRule

**Purpose**: Defines allowed state transitions and prerequisites

**Fields**:
- `from_status`: Source status (string, or "*" for any)
- `to_status`: Destination status (string)
- `issue_types`: Applicable issue types (list of strings)
- `prerequisites`: Required conditions (list of Prerequisite)
- `description`: Rule description (string)

**Validation Rules**:
- `from_status` must be non-empty
- `to_status` must be non-empty
- `issue_types` must not be empty
- `from_status` != `to_status` (no self-transitions)

### 9. Prerequisite

**Purpose**: Defines a condition that must be met for workflow transition

**Fields**:
- `type`: Prerequisite type (string: "field_present", "field_value", "approval", "custom")
- `parameters`: Type-specific parameters (dict[str, Any])
- `error_message`: Message shown when not met (string)

**Validation Rules**:
- `type` must be one of supported types
- `parameters` must contain required keys for type
- `error_message` must be non-empty

**Prerequisite Type Parameters**:
- `field_present`: `{field: str}`
- `field_value`: `{field: str, value: Any, operator: str}`
- `approval`: `{approver_role: str}`
- `custom`: `{expression: str}` (evaluated expression)

### 10. QualityCriteria

**Purpose**: Defines scoring rubrics for quality assessment

**Fields**:
- `dimensions`: Quality dimensions to assess (dict[str, DimensionCriteria])
- `weights`: Dimension weights for overall score (dict[str, float], sum to 1.0)
- `thresholds`: Score thresholds for quality levels (dict[str, float])

**Validation Rules**:
- `dimensions` must contain at least one dimension
- `weights` must sum to 1.0 (±0.01 tolerance)
- All dimension names in `weights` must exist in `dimensions`
- `thresholds` must contain "excellent", "good", "acceptable", "poor"

**Standard Dimensions**:
- `completeness`: Required fields and content presence
- `clarity`: Readability and understandability
- `formatting`: Markdown structure and style
- `standards`: Adherence to team conventions

### 11. DimensionCriteria

**Purpose**: Defines criteria for a single quality dimension

**Fields**:
- `name`: Dimension name (string)
- `description`: What this dimension measures (string)
- `metrics`: Metrics to evaluate (list of Metric)
- `scoring`: How to combine metric scores (string: "average", "weighted", "min", "max")

**Validation Rules**:
- `name` must be non-empty
- `metrics` must not be empty
- `scoring` must be one of supported methods

### 12. Metric

**Purpose**: Defines a single measurable quality metric

**Fields**:
- `name`: Metric name (string)
- `type`: Metric type (string: "presence", "length", "readability", "pattern", "custom")
- `parameters`: Type-specific parameters (dict[str, Any])
- `weight`: Metric weight within dimension (float, 0.0-1.0)
- `scoring_function`: How to convert raw value to score (string: "linear", "threshold", "custom")

**Validation Rules**:
- `name` must be non-empty
- `type` must be one of supported types
- `weight` must be 0.0-1.0
- `scoring_function` must be one of supported functions

### 13. EvaluationReport

**Purpose**: Output of ticket evaluation process

**Fields**:
- `ticket_key`: Evaluated ticket key (string)
- `guideline_version`: Guidelines version used (string)
- `timestamp`: Evaluation timestamp (datetime)
- `overall_status`: Compliance status (string: "pass", "fail", "warning")
- `compliance_result`: Guideline compliance details (ComplianceResult object)
- `quality_assessment`: Quality scores (QualityAssessment object)
- `violations`: List of violations (list of Violation)
- `recommendations`: Improvement suggestions (list of Recommendation)
- `metadata`: Evaluation metadata (EvaluationMetadata object)

**Validation Rules**:
- `ticket_key` must match Jira key pattern
- `guideline_version` must follow semantic versioning
- `timestamp` must be valid datetime
- `overall_status` must be one of allowed values

**Relationships**:
- Has one `compliance_result` (ComplianceResult)
- Has one `quality_assessment` (QualityAssessment)
- Has many `violations` (Violation)
- Has many `recommendations` (Recommendation)
- Has one `metadata` (EvaluationMetadata)

### 14. ComplianceResult

**Purpose**: Results of guideline compliance checking

**Fields**:
- `passed`: Whether ticket passes compliance (boolean)
- `required_fields_status`: Required field check results (dict[str, bool])
- `field_validation_status`: Field validation results (dict[str, bool])
- `workflow_status`: Workflow rule compliance (bool)
- `checked_rules`: Number of rules checked (integer)
- `passed_rules`: Number of rules passed (integer)
- `failed_rules`: Number of rules failed (integer)

**Validation Rules**:
- `checked_rules` >= `passed_rules` + `failed_rules`
- `passed` is true only if `failed_rules` == 0

### 15. QualityAssessment

**Purpose**: Quality scoring results across dimensions

**Fields**:
- `overall_score`: Combined quality score (float, 0-100)
- `quality_level`: Quality classification (string: "excellent", "good", "acceptable", "poor")
- `dimension_scores`: Scores by dimension (dict[str, float])
- `metric_scores`: Raw metric scores (dict[str, dict[str, float]])

**Validation Rules**:
- `overall_score` must be 0-100
- `quality_level` must be one of allowed values
- All scores in `dimension_scores` must be 0-100
- `quality_level` must match threshold for `overall_score`

### 16. Violation

**Purpose**: Represents a single guideline violation

**Fields**:
- `severity`: Violation severity (string: "error", "warning", "info")
- `category`: Violation category (string: "required_field", "validation", "workflow", "quality")
- `field_name`: Affected field (optional string)
- `guideline_section`: Reference to guideline section (string)
- `message`: Human-readable description (string)
- `current_value`: Actual field value (optional Any)
- `expected_value`: Expected value or format (optional Any)

**Validation Rules**:
- `severity` must be one of allowed values
- `category` must be one of allowed values
- `message` must be non-empty
- `guideline_section` must be non-empty

### 17. Recommendation

**Purpose**: Suggested improvement action

**Fields**:
- `priority`: Recommendation priority (string: "high", "medium", "low")
- `category`: Improvement category (string: "completeness", "clarity", "formatting", "standards")
- `title`: Short recommendation title (string)
- `description`: Detailed explanation (string)
- `example`: Example of improvement (optional string)
- `field_name`: Related field (optional string)

**Validation Rules**:
- `priority` must be one of allowed values
- `category` must be one of allowed values
- `title` must be 10-100 characters
- `description` must be non-empty

### 18. EvaluationMetadata

**Purpose**: Context and configuration of evaluation

**Fields**:
- `evaluator_version`: Tool version (string)
- `evaluation_duration`: Processing time in seconds (float)
- `configuration`: Evaluation configuration used (dict[str, Any])
- `warnings`: Non-fatal warnings (list of strings)
- `errors`: Non-fatal errors (list of strings)

**Validation Rules**:
- `evaluator_version` must follow semantic versioning
- `evaluation_duration` must be positive float

## State Transitions

### EvaluationReport Status Flow

```
[Start] → parsing_ticket → parsing_guidelines → evaluating_compliance
         → evaluating_quality → generating_recommendations → complete

Error states at any point → failed_*
```

**Valid Transitions**:
- `parsing_ticket` → `parsing_guidelines` or `failed_parse`
- `parsing_guidelines` → `evaluating_compliance` or `failed_parse`
- `evaluating_compliance` → `evaluating_quality` or `failed_evaluation`
- `evaluating_quality` → `generating_recommendations` or `failed_evaluation`
- `generating_recommendations` → `complete` or `failed_output`

## Validation Summary

### Cross-Entity Validation

1. **JiraIssue.issue_type ∈ ProcessGuidelines.applies_to**
   - Ensures guidelines apply to the ticket type

2. **Violation.field_name ∈ JiraIssue fields**
   - Violations reference valid ticket fields

3. **Recommendation.field_name ∈ JiraIssue fields**
   - Recommendations reference valid ticket fields

4. **QualityAssessment.quality_level matches threshold**
   - Quality level corresponds to overall_score thresholds

5. **ComplianceResult counts sum correctly**
   - `checked_rules` = `passed_rules` + `failed_rules`

### Business Rules

1. **Required Field Rule**: If RequiredField.required = true and JiraIssue missing field → create Violation(severity="error")

2. **Field Validation Rule**: If FieldValidation fails → create Violation(severity based on rule)

3. **Workflow Rule**: If WorkflowRule prerequisites not met → create Violation(severity="error")

4. **Quality Threshold Rule**: If dimension_score < acceptable_threshold → create Recommendation

5. **Overall Status Rule**:
   - `overall_status` = "fail" if any error violations
   - `overall_status` = "warning" if only warning violations
   - `overall_status` = "pass" if no violations

## Serialization Formats

All entities serialize to/from JSON using Pydantic's `.model_dump()` and `.model_validate()` methods.

**Standard Serialization**:
- Datetime fields: ISO 8601 format (e.g., "2025-11-26T10:30:00Z")
- Enums: String values
- Optional fields: Null if not present
- Collections: JSON arrays

**Custom Serialization**:
- JiraIssue description formats converted to plain text for analysis
- ProcessGuidelines loaded from markdown with YAML front matter
- EvaluationReport output formatted as JSON or human-readable text
