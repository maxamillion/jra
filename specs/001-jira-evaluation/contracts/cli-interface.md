# CLI Interface Contract

**Version**: 1.0.0
**Tool**: jra (Jira Review Agent)
**Protocol**: stdin/args → stdout (results), stderr (errors/warnings)

## Installation

```bash
pip install jra
```

## Commands

### 1. evaluate

**Purpose**: Evaluate a single Jira ticket against process guidelines

**Signature**:
```bash
jra evaluate [OPTIONS] TICKET GUIDELINES
```

**Arguments**:
- `TICKET`: Path to Jira ticket JSON file, or `-` for stdin
- `GUIDELINES`: Path to process guidelines markdown file

**Options**:
- `--format [json|human|markdown]`: Output format (default: human)
- `--color/--no-color`: Enable/disable colored output (default: auto-detect)
- `--timing`: Include performance timing in output
- `--config PATH`: Path to custom configuration file
- `--strict`: Fail on warnings (exit code 2)
- `--debug`: Enable debug logging to stderr
- `--version`: Show version and exit
- `--help`: Show help message and exit

**Exit Codes**:
- `0`: Success (ticket passes evaluation)
- `1`: Usage error (invalid arguments)
- `2`: Validation error (ticket fails evaluation or --strict warnings)
- `3`: Evaluation error (internal error during evaluation)

**Examples**:

```bash
# Basic evaluation
jra evaluate ticket.json guidelines.md

# JSON output for automation
jra evaluate ticket.json guidelines.md --format json > report.json

# Stdin input
cat ticket.json | jra evaluate - guidelines.md

# Strict mode (warnings are errors)
jra evaluate ticket.json guidelines.md --strict

# With timing metrics
jra evaluate ticket.json guidelines.md --timing
```

**Input (TICKET)**:
```json
{
  "id": "12345",
  "key": "PROJ-123",
  "fields": {
    "issuetype": {"name": "Story"},
    "status": {"name": "In Progress"},
    "summary": "Add user authentication",
    "description": "Detailed description...",
    "priority": {"name": "High"},
    "assignee": {"displayName": "John Doe"},
    "reporter": {"displayName": "Jane Smith"},
    "created": "2025-11-20T10:00:00Z",
    "updated": "2025-11-26T09:30:00Z"
  }
}
```

**Output (human format)**:
```
Jira Issue Evaluation Report
=============================

Ticket: PROJ-123
Guidelines: guidelines.md (v1.2.0)
Evaluated: 2025-11-26 10:30:45

Overall Status: FAIL ❌

Compliance Check
----------------
✓ Required fields: 8/10 present
✗ Field validations: 2/5 failed
✓ Workflow rules: Passed

Quality Assessment
------------------
Overall Score: 72/100 (Acceptable)

  Completeness:  85/100 ✓
  Clarity:       68/100 ⚠
  Formatting:    70/100 ⚠
  Standards:     65/100 ⚠

Violations (3)
--------------
[ERROR] Missing required field: acceptance_criteria
  Guideline: § 2.1 - All stories must have acceptance criteria
  Recommendation: Add acceptance criteria in Given-When-Then format

[ERROR] Field validation failed: description
  Current: 45 characters
  Expected: Minimum 100 characters
  Guideline: § 2.3 - Story descriptions must be detailed

[WARNING] Low clarity score for summary field
  Issue: Contains jargon without explanation
  Recommendation: Define technical terms or use simpler language

Recommendations (5)
-------------------
[HIGH] Add acceptance criteria
  Stories require testable acceptance criteria in Given-When-Then format.
  Example: "Given a logged-in user, When they click logout, Then their session ends"

[MEDIUM] Expand description
  Current description is too brief (45 chars). Add:
  - User context and motivation
  - Expected behavior details
  - Edge cases to consider

[MEDIUM] Improve summary clarity
  Replace jargon: "auth" → "authentication", "SSO" → "Single Sign-On"

[LOW] Add labels
  Consider adding labels: authentication, security, user-management

[LOW] Add story points
  Estimate complexity by adding story points field

Summary
-------
Evaluation completed in 0.8s
Next steps: Address 2 errors before ticket can proceed
```

**Output (json format)**:
```json
{
  "ticket_key": "PROJ-123",
  "guideline_version": "1.2.0",
  "timestamp": "2025-11-26T10:30:45Z",
  "overall_status": "fail",
  "compliance_result": {
    "passed": false,
    "required_fields_status": {
      "summary": true,
      "description": true,
      "acceptance_criteria": false,
      ...
    },
    "field_validation_status": {
      "description": false,
      "summary": false,
      ...
    },
    "workflow_status": true,
    "checked_rules": 15,
    "passed_rules": 13,
    "failed_rules": 2
  },
  "quality_assessment": {
    "overall_score": 72.0,
    "quality_level": "acceptable",
    "dimension_scores": {
      "completeness": 85.0,
      "clarity": 68.0,
      "formatting": 70.0,
      "standards": 65.0
    }
  },
  "violations": [
    {
      "severity": "error",
      "category": "required_field",
      "field_name": "acceptance_criteria",
      "guideline_section": "§ 2.1",
      "message": "Missing required field: acceptance_criteria",
      "current_value": null,
      "expected_value": "Given-When-Then format"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "category": "completeness",
      "title": "Add acceptance criteria",
      "description": "Stories require testable acceptance criteria...",
      "example": "Given a logged-in user, When...",
      "field_name": "acceptance_criteria"
    }
  ],
  "metadata": {
    "evaluator_version": "1.0.0",
    "evaluation_duration": 0.8,
    "configuration": {},
    "warnings": [],
    "errors": []
  }
}
```

---

### 2. batch

**Purpose**: Evaluate multiple Jira tickets in one operation

**Signature**:
```bash
jra batch [OPTIONS] TICKETS GUIDELINES
```

**Arguments**:
- `TICKETS`: Path to file containing ticket list (JSON array or JSONL), or `-` for stdin
- `GUIDELINES`: Path to process guidelines markdown file

**Options**:
- `--format [json|human|markdown]`: Output format (default: human)
- `--progress/--no-progress`: Show progress bar (default: auto-detect TTY)
- `--continue-on-error`: Continue evaluating even if some tickets fail
- `--parallel WORKERS`: Number of parallel evaluators (default: 1)
- `--timing`: Include performance timing in output
- `--config PATH`: Path to custom configuration file
- `--strict`: Fail on warnings (exit code 2)
- `--debug`: Enable debug logging to stderr
- `--help`: Show help message and exit

**Exit Codes**:
- `0`: Success (all tickets evaluated successfully)
- `1`: Usage error (invalid arguments)
- `2`: Validation error (one or more tickets failed or --strict warnings)
- `3`: Evaluation error (internal error during batch processing)

**Examples**:

```bash
# Basic batch evaluation
jra batch tickets.json guidelines.md

# With progress bar
jra batch tickets.json guidelines.md --progress

# Continue on errors
jra batch tickets.json guidelines.md --continue-on-error

# Parallel evaluation (4 workers)
jra batch tickets.json guidelines.md --parallel 4

# JSON output with aggregate stats
jra batch tickets.json guidelines.md --format json > batch-report.json
```

**Input (TICKETS)** - JSON array:
```json
[
  {
    "id": "12345",
    "key": "PROJ-123",
    "fields": {...}
  },
  {
    "id": "12346",
    "key": "PROJ-124",
    "fields": {...}
  }
]
```

**Input (TICKETS)** - JSONL (one ticket per line):
```
{"id": "12345", "key": "PROJ-123", "fields": {...}}
{"id": "12346", "key": "PROJ-124", "fields": {...}}
```

**Output (human format)**:
```
Batch Evaluation Report
=======================

Guidelines: guidelines.md (v1.2.0)
Evaluated: 2025-11-26 10:30:45
Tickets Processed: 10

Aggregate Statistics
--------------------
✓ Passed:   6 (60%)
✗ Failed:   3 (30%)
⚠ Warnings: 1 (10%)

Average Quality Score: 76.5/100
Average Evaluation Time: 0.9s per ticket

Compliance Summary
------------------
Required Fields: 85% average presence
Field Validations: 72% average pass rate
Workflow Rules: 95% compliance

Top Violations (by frequency)
------------------------------
1. Missing acceptance criteria (5 tickets)
2. Description too brief (4 tickets)
3. Missing story points (3 tickets)

Quality Distribution
--------------------
Excellent: 2 tickets (20%)
Good:      4 tickets (40%)
Acceptable: 3 tickets (30%)
Poor:      1 ticket (10%)

Individual Results
------------------
PROJ-123: FAIL ❌ (Score: 72/100) - 2 errors, 1 warning
PROJ-124: PASS ✓ (Score: 88/100) - 0 errors, 1 warning
PROJ-125: PASS ✓ (Score: 92/100) - 0 errors, 0 warnings
PROJ-126: FAIL ❌ (Score: 65/100) - 3 errors, 2 warnings
...

Summary
-------
Batch evaluation completed in 9.2s
Recommendation: Focus on acceptance criteria and description quality
```

**Output (json format)**:
```json
{
  "guideline_version": "1.2.0",
  "timestamp": "2025-11-26T10:30:45Z",
  "aggregate_stats": {
    "total_tickets": 10,
    "passed": 6,
    "failed": 3,
    "warnings": 1,
    "average_quality_score": 76.5,
    "average_duration": 0.9
  },
  "compliance_summary": {
    "required_fields_avg": 0.85,
    "field_validations_avg": 0.72,
    "workflow_compliance": 0.95
  },
  "top_violations": [
    {"violation": "Missing acceptance criteria", "count": 5},
    {"violation": "Description too brief", "count": 4},
    {"violation": "Missing story points", "count": 3}
  ],
  "quality_distribution": {
    "excellent": 2,
    "good": 4,
    "acceptable": 3,
    "poor": 1
  },
  "results": [
    {
      "ticket_key": "PROJ-123",
      "overall_status": "fail",
      "quality_assessment": {"overall_score": 72.0},
      "violations_count": 3,
      "evaluation_duration": 0.8
    },
    ...
  ],
  "metadata": {
    "evaluator_version": "1.0.0",
    "total_duration": 9.2,
    "configuration": {},
    "errors": []
  }
}
```

---

## Configuration File

**Location**: `~/.jra/config.toml` or specified via `--config`

**Format**: TOML

**Example**:
```toml
[evaluation]
strict_mode = false
default_format = "human"
enable_color = true
show_timing = false

[quality]
completeness_weight = 0.30
clarity_weight = 0.30
formatting_weight = 0.20
standards_weight = 0.20

[quality.thresholds]
excellent = 90.0
good = 75.0
acceptable = 60.0
poor = 0.0

[output]
max_recommendations = 10
include_examples = true
verbose_violations = true

[batch]
default_workers = 4
continue_on_error = false
show_progress = true
```

---

## Environment Variables

- `JRA_CONFIG`: Path to configuration file
- `JRA_GUIDELINES`: Default guidelines path
- `JRA_FORMAT`: Default output format
- `NO_COLOR`: Disable colored output (standard)
- `JRA_DEBUG`: Enable debug logging
- `JRA_STRICT`: Enable strict mode

---

## Error Handling

### Error Messages (stderr)

```bash
# Missing argument
Error: Missing argument 'TICKET'
Usage: jra evaluate [OPTIONS] TICKET GUIDELINES

# Invalid file
Error: Cannot read ticket file: No such file or directory
  File: /path/to/ticket.json

# Parse error
Error: Invalid JSON in ticket file
  File: /path/to/ticket.json
  Line: 15, Column: 23
  Issue: Unexpected token '}'

# Validation error
Error: Invalid guideline format
  File: /path/to/guidelines.md
  Issue: Missing required section 'Required Fields'

# Internal error
Error: Evaluation failed
  Ticket: PROJ-123
  Cause: UnexpectedEvaluationError

  Run with --debug for full traceback
```

### Exit Codes Summary

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Ticket passed all checks |
| 1 | Usage error | Missing required argument |
| 2 | Validation error | Ticket failed evaluation |
| 3 | Evaluation error | Internal processing error |

---

## Version Information

```bash
$ jra --version
jra, version 1.0.0
Python 3.11.5
```
