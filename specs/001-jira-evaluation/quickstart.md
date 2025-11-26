# Quickstart Guide: Jira Issue Evaluation AI Agent

**Version**: 1.0.0
**Last Updated**: 2025-11-26

## Overview

The Jira Review Agent (jra) is a command-line tool that evaluates Jira issue tickets against your team's process guidelines. It checks compliance, assesses quality, and provides actionable recommendations for improvement.

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Install from PyPI

```bash
pip install jra
```

### Verify Installation

```bash
jra --version
```

Expected output:
```
jra, version 1.0.0
Python 3.11.x
```

## Quick Start (5 minutes)

### Step 1: Prepare Your Inputs

You need two files:

1. **Jira Ticket** (JSON format - exported from Jira API)
2. **Process Guidelines** (Markdown format - your team's standards)

### Step 2: Create Sample Files

**Create `ticket.json`**:
```json
{
  "id": "12345",
  "key": "DEMO-1",
  "fields": {
    "issuetype": {"name": "Story"},
    "status": {"name": "To Do"},
    "summary": "Add user login feature",
    "description": "We need a login page for users",
    "priority": {"name": "High"},
    "reporter": {"displayName": "Jane Smith"},
    "created": "2025-11-26T09:00:00Z",
    "updated": "2025-11-26T09:00:00Z"
  }
}
```

**Create `guidelines.md`**:
```markdown
---
version: 1.0.0
last_updated: 2025-11-26
applies_to: [Story, Bug, Task]
---

# Team Process Guidelines

## Required Fields

All Stories must have:
- Summary (10-255 characters)
- Description (minimum 100 characters)
- Acceptance Criteria (Given-When-Then format)

All Bugs must have:
- Summary
- Description
- Steps to Reproduce
- Expected vs Actual Behavior

## Quality Standards

### Description Quality
- Minimum 100 characters
- Must include user context and motivation
- Should explain the "why" not just the "what"

### Acceptance Criteria
- Use Given-When-Then format
- At least 1 scenario required
- Scenarios must be testable

## Workflow Rules

Stories in "To Do" status must have:
- Complete description
- Acceptance criteria defined
- Story points estimated
```

### Step 3: Run Your First Evaluation

```bash
jra evaluate ticket.json guidelines.md
```

**Output**:
```
Jira Issue Evaluation Report
=============================

Ticket: DEMO-1
Guidelines: guidelines.md (v1.0.0)
Evaluated: 2025-11-26 10:30:45

Overall Status: FAIL ❌

Compliance Check
----------------
✗ Required fields: 2/3 present
✓ Field validations: Passed
✗ Workflow rules: 1 violation

Quality Assessment
------------------
Overall Score: 45/100 (Poor)

  Completeness:  33/100 ✗
  Clarity:       55/100 ⚠
  Formatting:    50/100 ⚠
  Standards:     42/100 ✗

Violations (3)
--------------
[ERROR] Missing required field: acceptance_criteria
  Guideline: § Required Fields - All Stories must have
  Recommendation: Add acceptance criteria in Given-When-Then format

[ERROR] Field validation failed: description
  Current: 30 characters
  Expected: Minimum 100 characters
  Guideline: § Quality Standards - Description Quality

[ERROR] Workflow rule violation
  Issue: Story in "To Do" missing story points
  Guideline: § Workflow Rules

Recommendations (4)
-------------------
[HIGH] Add acceptance criteria
  Stories require testable acceptance criteria in Given-When-Then format.
  Example: "Given a user on login page, When they enter valid credentials, Then they are logged in"

[HIGH] Expand description
  Current description is too brief (30 chars). Include:
  - User context and motivation (who needs this and why)
  - Expected behavior details
  - Edge cases to consider

[MEDIUM] Add story points
  Estimate complexity by adding story points field

[LOW] Improve description context
  Add "why" this feature is needed, not just "what" is being built

Summary
-------
Evaluation completed in 0.3s
Next steps: Address 3 errors before ticket can proceed
```

### Step 4: Fix the Ticket

Update `ticket.json` with the recommendations:

```json
{
  "id": "12345",
  "key": "DEMO-1",
  "fields": {
    "issuetype": {"name": "Story"},
    "status": {"name": "To Do"},
    "summary": "Add user login feature",
    "description": "As a user, I want to securely log in to the application so that I can access my personalized dashboard and protected data. This feature is critical for user account management and security compliance. The login should support email/password authentication initially, with plans for SSO in the future.",
    "customfield_10001": "Given a user on the login page, When they enter valid credentials, Then they are logged in and redirected to their dashboard\nGiven a user enters invalid credentials, When they submit the form, Then they see an error message and remain on the login page",
    "customfield_10002": 5,
    "priority": {"name": "High"},
    "reporter": {"displayName": "Jane Smith"},
    "created": "2025-11-26T09:00:00Z",
    "updated": "2025-11-26T10:00:00Z"
  }
}
```

### Step 5: Re-evaluate

```bash
jra evaluate ticket.json guidelines.md
```

**Output**:
```
Jira Issue Evaluation Report
=============================

Ticket: DEMO-1
Overall Status: PASS ✓

Quality Assessment
------------------
Overall Score: 88/100 (Good)

  Completeness:  95/100 ✓
  Clarity:       85/100 ✓
  Formatting:    82/100 ✓
  Standards:     90/100 ✓

Recommendations (1)
-------------------
[LOW] Consider adding labels
  Suggested: authentication, user-management, security

Summary
-------
Evaluation completed in 0.3s
Ticket meets all requirements!
```

## Common Use Cases

### Use Case 1: Batch Evaluation

Evaluate multiple tickets at once:

```bash
# Create tickets.json with array of tickets
jra batch tickets.json guidelines.md

# With progress bar
jra batch tickets.json guidelines.md --progress

# JSON output for automation
jra batch tickets.json guidelines.md --format json > report.json
```

### Use Case 2: CI/CD Integration

Integrate into your CI pipeline:

```bash
#!/bin/bash
# check-jira-quality.sh

# Export ticket from Jira API
curl -X GET "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123" \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  > ticket.json

# Evaluate ticket
jra evaluate ticket.json guidelines.md --format json --strict

# Exit code 0 = pass, 2 = fail
exit $?
```

### Use Case 3: Custom Configuration

Create `~/.jra/config.toml`:

```toml
[evaluation]
strict_mode = true
default_format = "human"

[quality.thresholds]
excellent = 95.0
good = 80.0
acceptable = 65.0

[output]
max_recommendations = 5
```

Run with custom config:

```bash
jra evaluate ticket.json guidelines.md --config ~/.jra/config.toml
```

### Use Case 4: JSON Output for Automation

```bash
# Generate JSON report
jra evaluate ticket.json guidelines.md --format json > report.json

# Parse with jq
cat report.json | jq '.overall_status'  # "pass" or "fail"
cat report.json | jq '.quality_assessment.overall_score'  # 88.0
cat report.json | jq '.violations[] | select(.severity == "error")'
```

## Guidelines Best Practices

### 1. Use Semantic Versioning

```markdown
---
version: 2.1.0
last_updated: 2025-11-26
---
```

Increment:
- **MAJOR** (2.0.0): Breaking changes to required fields
- **MINOR** (2.1.0): New optional requirements added
- **PATCH** (2.1.1): Clarifications, typo fixes

### 2. Be Specific and Testable

**Bad**:
```markdown
- Description should be good quality
```

**Good**:
```markdown
- Description minimum 100 characters
- Must include user context and motivation
- Should explain the "why" not just the "what"
```

### 3. Provide Examples

```markdown
### Acceptance Criteria Format

**Required**: Given-When-Then format

**Example**:
```
Given a logged-in user
When they click the logout button
Then their session ends and they're redirected to login page
```
```

### 4. Organize by Issue Type

```markdown
## Story Requirements
- Acceptance criteria (Given-When-Then)
- User context and motivation
- Story points estimated

## Bug Requirements
- Steps to reproduce
- Expected vs actual behavior
- Environment details
```

## Troubleshooting

### Error: Cannot read ticket file

**Problem**: File not found or invalid path

**Solution**:
```bash
# Check file exists
ls -la ticket.json

# Use absolute path
jra evaluate /full/path/to/ticket.json guidelines.md
```

### Error: Invalid JSON in ticket file

**Problem**: Malformed JSON

**Solution**:
```bash
# Validate JSON with jq
cat ticket.json | jq .

# Or use Python
python -m json.tool ticket.json
```

### Error: Missing required section in guidelines

**Problem**: Guidelines file missing expected sections

**Solution**:
Ensure your guidelines.md includes:
- Required Fields section
- Quality Standards section (optional but recommended)
- Workflow Rules section (if applicable)

### Low Quality Scores

**Problem**: Tickets scoring poorly despite meeting requirements

**Solution**:
- Check `dimension_scores` to see which area is low
- Review recommendations for specific improvements
- Use `--debug` to see detailed scoring breakdown

## Next Steps

1. **Customize Guidelines**: Adapt the sample guidelines to your team's standards
2. **Integrate with Jira**: Use Jira API to export tickets programmatically
3. **Automate**: Add to CI/CD pipeline for automated quality checks
4. **Iterate**: Refine guidelines based on evaluation results

## Getting Help

```bash
# View help
jra --help
jra evaluate --help
jra batch --help

# Enable debug mode
jra evaluate ticket.json guidelines.md --debug

# Check version
jra --version
```

## Example Files

Complete example files are available in the project repository:

- `examples/tickets/` - Sample Jira tickets (good and bad)
- `examples/guidelines/` - Sample process guidelines
- `examples/reports/` - Expected output examples
- `examples/ci-cd/` - CI/CD integration scripts

## Additional Resources

- [CLI Interface Documentation](contracts/cli-interface.md)
- [Input Schema Reference](contracts/input-schema.json)
- [Output Schema Reference](contracts/output-schema.json)
- [Configuration Guide](docs/configuration.md)
- [Guidelines Writing Guide](docs/guidelines.md)
- [API Reference](docs/api.md)
