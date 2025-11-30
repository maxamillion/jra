# Comprehensive Team Process Guidelines

Version: 2.0.0
Last Updated: 2025-11-26
Team: Engineering

## Table of Contents

1. [Overview](#overview)
2. [Required Fields](#required-fields)
3. [Field Validations](#field-validations)
4. [Workflow Rules](#workflow-rules)
5. [Quality Standards](#quality-standards)
6. [Story Types](#story-types)

## Overview

This document defines the comprehensive process guidelines for Jira ticket creation, management, and quality standards. All team members must follow these guidelines to ensure consistency and quality across our project management.

### Purpose

- Ensure complete and accurate ticket information
- Maintain consistent quality standards
- Enable effective sprint planning and execution
- Facilitate clear communication across teams

## Required Fields

All Jira tickets MUST include the following fields:

### Universal Required Fields

- **Summary**: Brief, descriptive title (max 120 characters)
- **Description**: Detailed explanation of the work
- **Issue Type**: Story, Bug, Task, Epic
- **Priority**: Blocker, Critical, Major, Minor, Trivial
- **Reporter**: Person who created the ticket
- **Project**: Target project key

### Story-Specific Required Fields

For Issue Type = "Story":

- **Story Points**: Effort estimate (Fibonacci: 1, 2, 3, 5, 8, 13)
- **Acceptance Criteria**: Measurable success criteria
- **User Story**: As a [role], I want [feature], so that [benefit]

### Bug-Specific Required Fields

For Issue Type = "Bug":

- **Steps to Reproduce**: Numbered list of reproduction steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, browser, version information
- **Severity**: Impact assessment

### Epic-Specific Required Fields

For Issue Type = "Epic":

- **Epic Name**: Short name for the epic
- **Epic Description**: High-level overview
- **Success Criteria**: Measurable epic-level outcomes
- **Timeline**: Expected start and end dates

## Field Validations

### Summary Validation

**Requirements**:
- Length: 10-120 characters
- Format: Start with capital letter
- Content: No generic terms like "fix bug" or "update code"
- Quality: Descriptive and specific

**Good Examples**:
- "Add user authentication with OAuth2"
- "Fix memory leak in image processing pipeline"
- "Implement real-time notifications for chat"

**Bad Examples**:
- "Bug fix" (too vague)
- "Update" (not descriptive)
- "This is a really long summary that goes on and on and provides way too much detail that should be in the description field instead" (too long)

### Description Validation

**Requirements**:
- Minimum length: 50 characters
- Structure: Include context, details, and impact
- Format: Use markdown formatting for clarity
- Links: Reference related tickets, documentation, or resources

**Required Sections for Stories**:
```markdown
## Background
[Context and motivation]

## Requirements
- Functional requirement 1
- Functional requirement 2
- Non-functional requirement 1

## Technical Approach
[High-level implementation strategy]

## Dependencies
- Dependency 1
- Dependency 2
```

**Required Sections for Bugs**:
```markdown
## Problem Description
[What's broken and impact]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Observed issue

## Expected vs Actual Behavior
**Expected**: [What should happen]
**Actual**: [What happens instead]

## Additional Context
[Screenshots, logs, related tickets]
```

### Priority Validation

**Blocker**:
- Production is down or severely impacted
- Blocks all team members from working
- Revenue loss or security breach
- Requires immediate attention

**Critical**:
- Major functionality broken
- Blocks significant portion of users
- High business impact
- Must be addressed in current sprint

**Major**:
- Important feature not working as expected
- Workaround exists but is inconvenient
- Should be addressed soon

**Minor**:
- Small issue with minimal impact
- Nice-to-have improvement
- Can be scheduled normally

**Trivial**:
- Cosmetic issue
- Very low impact
- Can be addressed when convenient

### Story Points Validation

**Requirements**:
- Use Fibonacci sequence: 1, 2, 3, 5, 8, 13
- Based on complexity, not time
- Include testing and review effort
- Re-estimate if unknowns discovered

**Guidelines**:
- **1 point**: Trivial change, well understood, < 2 hours
- **2 points**: Simple change, clear requirements, < 4 hours
- **3 points**: Moderate complexity, some unknowns, < 1 day
- **5 points**: Complex change, multiple components, 1-2 days
- **8 points**: Very complex, significant unknowns, 2-3 days
- **13 points**: Should be split into smaller stories

## Workflow Rules

### Status Transitions

**Valid Transitions**:

```
Backlog → To Do → In Progress → In Review → Done
         ↓        ↑
         └─ Blocked ─┘
```

**Status Definitions**:

- **Backlog**: Not yet prioritized for a sprint
- **To Do**: Prioritized and ready to start
- **In Progress**: Actively being worked on
- **Blocked**: Work stopped due to dependency
- **In Review**: Code review or testing in progress
- **Done**: Completed and verified

### Required Transitions

1. **Backlog → To Do**:
   - Must have: Story points, Acceptance criteria
   - Must be: Fully specified and estimated
   - Assigned to: Sprint

2. **To Do → In Progress**:
   - Must have: Assignee
   - Should have: Started date logged
   - Update: Add comment with approach

3. **In Progress → In Review**:
   - Must have: Pull request link
   - Must have: All acceptance criteria addressed
   - Update: Add implementation notes

4. **In Review → Done**:
   - Must have: Code review approval (≥2 approvals)
   - Must have: All tests passing
   - Must have: QA sign-off (for bugs and stories)
   - Update: Add verification notes

5. **Any → Blocked**:
   - Must have: Blocker description in comments
   - Must have: Link to blocking ticket or external issue
   - Must have: Estimated unblock date

### Time Tracking Rules

- Log work daily (minimum)
- Include detailed work descriptions
- Track time in 15-minute increments
- Remaining estimate must be updated when logging work
- Original estimate should never change

## Quality Standards

### Definition of Ready (Before Sprint)

A ticket is ready for sprint planning when:

- [ ] All required fields are populated
- [ ] Description is complete and clear
- [ ] Acceptance criteria are specific and testable
- [ ] Dependencies are identified and linked
- [ ] Story points are estimated
- [ ] No blocking issues
- [ ] Technical approach is feasible

### Definition of Done

A ticket is considered done when:

- [ ] All acceptance criteria are met
- [ ] Code is reviewed and approved (≥2 reviewers)
- [ ] Unit tests written and passing (≥80% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] QA verification complete (for stories and bugs)
- [ ] Performance requirements met
- [ ] Security review complete (for security-related changes)
- [ ] Deployed to staging environment
- [ ] Product owner acceptance received

### Acceptance Criteria Format

Use **Given-When-Then** format:

```
Given [precondition/context]
When [action/event]
Then [expected outcome]
```

**Example**:
```
Given a user is logged in
When they click the "Logout" button
Then they are redirected to the login page
And their session is terminated
And they cannot access protected pages
```

## Story Types

### User Story

**Purpose**: Deliver value to end users

**Template**:
```
As a [type of user]
I want [goal/desire]
So that [benefit/value]
```

**Requirements**:
- Must provide user value
- Must have acceptance criteria
- Must be completable in one sprint
- Must be independently testable

### Bug

**Purpose**: Fix defects in existing functionality

**Requirements**:
- Must include reproduction steps
- Must include expected vs actual behavior
- Must include environment details
- Must link to original story (if applicable)
- Must have severity assessment

### Task

**Purpose**: Technical work that doesn't directly deliver user value

**Examples**:
- Infrastructure setup
- Refactoring
- Technical debt reduction
- Configuration changes

**Requirements**:
- Must explain technical necessity
- Must have clear completion criteria
- Should estimate effort

### Epic

**Purpose**: Large initiatives spanning multiple sprints

**Requirements**:
- Must break down into multiple stories
- Must have high-level success criteria
- Must have business justification
- Should have timeline estimate
- Should identify key stakeholders

## Labeling Conventions

### Required Labels

- **Component**: `frontend`, `backend`, `database`, `infrastructure`, `mobile`
- **Team**: `team-alpha`, `team-beta`, `team-gamma`
- **Type**: `feature`, `bugfix`, `refactor`, `hotfix`, `tech-debt`

### Optional Labels

- **Technology**: `react`, `python`, `postgres`, `docker`, `kubernetes`
- **Impact**: `breaking-change`, `security`, `performance`, `ux-improvement`
- **Sprint**: `sprint-planning`, `carry-over`, `stretch-goal`

## Review Checklist

Before moving a ticket to "In Progress", verify:

- [ ] Summary is clear and specific
- [ ] Description provides sufficient context
- [ ] All required fields for ticket type are populated
- [ ] Acceptance criteria are testable
- [ ] Story points are estimated (for stories)
- [ ] Priority is appropriate
- [ ] Labels are applied
- [ ] Dependencies are linked
- [ ] Assignee is set
- [ ] Sprint is assigned

## Compliance

Tickets that do not meet these guidelines will be:

1. Flagged with `needs-refinement` label
2. Commented with specific deficiencies
3. Moved back to Backlog status
4. Reassigned to reporter for updates

Team leads will review compliance weekly and report metrics to management.

## References

- [Jira Best Practices Guide](https://confluence.example.com/jira-best-practices)
- [Story Writing Workshop](https://confluence.example.com/story-workshop)
- [Definition of Done](https://confluence.example.com/dod)
- [Estimation Guidelines](https://confluence.example.com/estimation)
