<!--
Sync Impact Report:
===================
Version Change: N/A (initial version) → 1.0.0
Modified Principles: N/A (new constitution)
Added Sections:
  - Core Principles (4 principles: Code Quality First, Testing Standards, UX Consistency, Performance Requirements)
  - Quality Standards
  - Development Workflow
  - Governance
Removed Sections: N/A (new constitution)
Templates Status:
  ✅ .specify/templates/plan-template.md - Reviewed, compatible
  ✅ .specify/templates/spec-template.md - Reviewed, compatible
  ✅ .specify/templates/tasks-template.md - Reviewed, compatible
  ✅ .claude/commands/speckit.*.md - No command files found
Follow-up TODOs:
  - None - all placeholders filled
===================
-->

# Jira Review Agent Constitution

## Core Principles

### I. Code Quality First

Every line of code MUST meet these non-negotiable quality standards:

- **Readability**: Code must be self-documenting with clear naming and logical structure
- **Maintainability**: Follow DRY (Don't Repeat Yourself) and SOLID principles consistently
- **Type Safety**: Use static typing where available; all function signatures must have explicit types
- **Error Handling**: All error paths must be explicitly handled; no silent failures permitted
- **Documentation**: Public APIs, complex algorithms, and non-obvious logic require inline documentation
- **Linting**: All code must pass configured linters with zero warnings before commit
- **Code Review**: No code reaches production without peer review approval

**Rationale**: High code quality reduces technical debt, minimizes bugs, and accelerates long-term development velocity. Poor code quality compounds exponentially over time.

### II. Testing Standards (NON-NEGOTIABLE)

Testing is mandatory and follows strict Test-Driven Development (TDD) practices:

- **TDD Cycle**: Tests written → User approved → Tests fail → Implementation → Tests pass
- **Coverage Requirements**:
  - Unit tests: ≥80% code coverage for all business logic
  - Integration tests: ≥70% coverage for inter-component interactions
  - Contract tests: Required for all API endpoints and external integrations
- **Test Independence**: Tests must be isolated, idempotent, and executable in any order
- **Fast Feedback**: Unit test suite must complete in <10 seconds; integration tests in <60 seconds
- **Regression Prevention**: All bug fixes require corresponding regression tests before merge
- **Test Quality**: Tests must be clear, maintainable, and test one logical concept each

**Rationale**: TDD enforces design thinking upfront, prevents regressions, enables safe refactoring, and serves as living documentation. Non-negotiable because quality without tests is impossible to verify or maintain.

### III. User Experience Consistency

All user-facing interfaces must deliver consistent, predictable experiences:

- **Interface Contracts**: CLI tools follow text in/out protocol (stdin/args → stdout, errors → stderr)
- **Output Formats**: Support both JSON (machine-readable) and human-readable formats
- **Error Messages**: Clear, actionable error messages that guide users to resolution
- **Progress Feedback**: Long-running operations (>2s) must provide progress indicators
- **Backward Compatibility**: User-facing APIs maintain backward compatibility; breaking changes require MAJOR version bump
- **Accessibility**: Text-based interfaces must work with standard terminal accessibility tools
- **Documentation**: User-facing features require usage examples and clear documentation

**Rationale**: Consistent UX reduces cognitive load, builds user trust, and minimizes support burden. Inconsistent interfaces fragment user knowledge and create frustration.

### IV. Performance Requirements

System performance directly impacts user satisfaction and must meet these standards:

- **Response Time**: Interactive operations (user waiting) complete in <200ms p95
- **Throughput**: Batch operations process ≥100 items/second for typical workloads
- **Resource Usage**: Memory consumption stays <500MB for normal operations; <2GB peak
- **Scalability**: System gracefully handles 10x expected load without architectural changes
- **Efficiency**: Optimize critical paths; profile before optimizing; measure impact after
- **Degradation**: Performance degradation must be graceful; never fail silently under load
- **Monitoring**: Performance-critical operations include timing instrumentation

**Rationale**: Performance issues compound user frustration and limit system utility. Setting clear performance requirements ensures they're considered during design, not retrofitted afterward.

## Quality Standards

### Code Review Requirements

All code changes require review before merge:

- Minimum one approving review from team member familiar with affected code
- Review checklist: functionality, tests, documentation, performance, security
- Reviews focus on: correctness, maintainability, design patterns, edge cases
- Constructive feedback required; nitpicks clearly labeled as such
- Reviews completed within 24 hours; blockers escalated immediately

### Continuous Integration Gates

CI pipeline enforces quality gates automatically:

- **Build**: Code must compile/build successfully across all supported platforms
- **Linting**: Zero linting errors or warnings permitted
- **Type Checking**: Static type analysis must pass without errors
- **Security Scanning**: Automated security scans must show no critical/high vulnerabilities
- **Test Execution**: All test suites must pass (unit, integration, contract)
- **Coverage**: Coverage thresholds enforced (80% unit, 70% integration)
- **Performance**: Benchmark tests verify no >10% performance regression

### Security Requirements

Security is built-in, not bolted-on:

- All external inputs validated and sanitized
- Secrets never committed to source control; use environment variables/key management
- Dependencies scanned for known vulnerabilities; critical/high CVEs addressed within 7 days
- Authentication/authorization implemented for sensitive operations
- Audit logging for security-relevant events
- Security reviews required for authentication, authorization, data handling, and external integrations

## Development Workflow

### Feature Development Process

1. **Specification**: Create feature spec following `.specify/templates/spec-template.md`
2. **Planning**: Generate implementation plan via `/speckit.plan` command
3. **Constitution Check**: Verify compliance with all constitutional principles
4. **Test Creation**: Write failing tests covering acceptance criteria (TDD)
5. **Implementation**: Implement feature to pass tests
6. **Quality Gates**: Run full CI pipeline locally before pushing
7. **Review**: Submit for peer review with passing CI
8. **Merge**: Squash merge after approval and passing CI

### Test-First Development

Strict adherence to TDD cycle:

1. Write test describing desired behavior
2. Verify test fails (red)
3. Implement minimal code to pass test (green)
4. Refactor while keeping tests green (refactor)
5. Commit only when all tests pass

### Versioning and Breaking Changes

Semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to public APIs or user-facing interfaces
- **MINOR**: New features, backward-compatible enhancements
- **PATCH**: Bug fixes, internal improvements, documentation updates

Breaking changes require:
- Deprecation warnings in previous MINOR version when possible
- Migration guide documenting upgrade path
- User communication via changelog and release notes

## Governance

This constitution supersedes all other development practices and guidelines. All team members must understand and follow these principles.

### Amendment Process

Constitutional amendments require:

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Team review and discussion of proposal
3. **Approval**: Consensus approval from team (or majority if consensus impossible)
4. **Migration**: Update all affected templates, documentation, and code
5. **Communication**: Announce change to all stakeholders

### Compliance Verification

- All pull requests reviewed for constitutional compliance
- Template updates (`/speckit.plan`, `/speckit.tasks`) enforce constitution
- Quarterly constitution review to identify gaps or needed updates
- Violations require justification in Complexity Tracking section of plan.md

### Complexity Justification

When constitutional principles must be violated:

- Document specific violation and why it's necessary
- Explore and document simpler alternatives that were rejected
- Include mitigation plan to minimize negative impact
- Revisit periodically to determine if violation still necessary

**Version**: 1.0.0 | **Ratified**: 2025-11-26 | **Last Amended**: 2025-11-26
