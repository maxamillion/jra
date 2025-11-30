# Tasks: Jira Issue Evaluation AI Agent

**Input**: Design documents from `/specs/001-jira-evaluation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Per constitution (TDD is NON-NEGOTIABLE), tests are REQUIRED and must be written BEFORE implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Python project structure with src/jra/ layout per plan.md
- [X] T002 [P] Initialize pyproject.toml with project metadata, dependencies (Click, Pydantic, python-markdown, PyYAML)
- [X] T003 [P] Configure development tools in pyproject.toml (Black, Flake8, mypy, isort, pytest, pytest-cov)
- [X] T004 [P] Create README.md with installation instructions and quick start
- [X] T005 [P] Create LICENSE file (choose appropriate license)
- [X] T006 [P] Setup .gitignore for Python projects (venv, __pycache__, .pytest_cache, .coverage, dist, build)
- [X] T007 [P] Create GitHub Actions CI workflow (.github/workflows/ci.yml) for build, lint, type-check, test, coverage
- [X] T008 [P] Create pytest configuration in pyproject.toml with coverage thresholds (80% unit, 70% integration)
- [X] T009 [P] Create tests/conftest.py with pytest configuration and shared fixtures
- [X] T010 [P] Create test fixtures directory structure (tests/fixtures/guidelines/, tests/fixtures/tickets/, tests/fixtures/reports/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 [P] Create src/jra/__init__.py with package version export
- [X] T012 [P] Create src/jra/__main__.py entry point for `python -m jra`
- [X] T013 [P] Create src/jra/utils/__init__.py
- [X] T014 [P] Implement configuration management in src/jra/utils/config.py with TOML parsing and hierarchy
- [X] T015 [P] Implement logging setup in src/jra/utils/logging.py with level control and formatting
- [X] T016 [P] Implement timing utilities in src/jra/utils/timing.py for performance metrics
- [X] T017 [P] Create custom exception hierarchy in src/jra/utils/exceptions.py (JRAException, ParseError, ValidationError, EvaluationError, OutputError)
- [X] T018 [P] Write unit tests for utils in tests/unit/test_utils.py (config, logging, timing, exceptions)
- [X] T019 Create sample test fixtures in tests/fixtures/guidelines/comprehensive-guidelines.md
- [X] T020 [P] Create sample test fixtures in tests/fixtures/tickets/ (valid-story.json, invalid-bug.json, edge-cases/)
- [X] T021 [P] Create CLI base structure src/jra/cli/__init__.py
- [X] T022 Implement Click application root in src/jra/cli/main.py with version and help

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Issue Evaluation (Priority: P1) 🎯 MVP

**Goal**: Evaluate single Jira ticket against guidelines, produce compliance report with violations

**Independent Test**: Provide sample Jira JSON and guidelines markdown, verify report contains compliance status, violations with specific references, and quality scores

### Tests for User Story 1 (TDD - Write these FIRST) ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US1] Write contract test for Jira JSON input validation in tests/unit/test_parsers.py::test_jira_parser_valid_input
- [ ] T024 [P] [US1] Write contract test for guidelines markdown parsing in tests/unit/test_parsers.py::test_markdown_parser_valid_guidelines
- [ ] T025 [P] [US1] Write contract test for evaluation report JSON output in tests/unit/test_formatters.py::test_json_formatter_output_schema
- [ ] T026 [P] [US1] Write integration test for evaluate command in tests/integration/test_cli_evaluate.py::test_evaluate_command_basic_flow
- [ ] T027 [P] [US1] Write integration test for violation detection in tests/integration/test_evaluation_flow.py::test_violation_detection_and_reporting

### Implementation for User Story 1

**Models (Pydantic data models)**:

- [ ] T028 [P] [US1] Create base Pydantic models in src/jra/models/__init__.py
- [ ] T029 [P] [US1] Implement JiraIssue model in src/jra/models/jira.py with User, Comment, Attachment nested models
- [ ] T030 [P] [US1] Implement ProcessGuidelines model in src/jra/models/guidelines.py with RequiredField, FieldValidation, WorkflowRule nested models
- [ ] T031 [P] [US1] Implement Violation model in src/jra/models/violation.py with severity levels and categories
- [ ] T032 [P] [US1] Implement ComplianceResult model in src/jra/models/report.py
- [ ] T033 [P] [US1] Implement EvaluationReport model in src/jra/models/report.py with ComplianceResult, Violation list, metadata
- [ ] T034 [P] [US1] Write unit tests for Jira models in tests/unit/test_models.py::test_jira_issue_validation
- [ ] T035 [P] [US1] Write unit tests for Guidelines models in tests/unit/test_models.py::test_process_guidelines_validation
- [ ] T036 [P] [US1] Write unit tests for Report models in tests/unit/test_models.py::test_evaluation_report_validation

**Parsers (Input parsing and validation)**:

- [ ] T037 [US1] Implement Jira JSON parser in src/jra/parsers/jira_parser.py to convert API JSON to JiraIssue model (depends on T029)
- [ ] T038 [US1] Implement markdown parser in src/jra/parsers/markdown_parser.py to extract ProcessGuidelines from markdown (depends on T030)
- [ ] T039 [P] [US1] Implement JSON schema validator in src/jra/parsers/schema_validator.py for input/output contracts
- [ ] T040 [P] [US1] Write unit tests for Jira parser in tests/unit/test_parsers.py::test_jira_parser_field_extraction
- [ ] T041 [P] [US1] Write unit tests for markdown parser in tests/unit/test_parsers.py::test_markdown_parser_guideline_extraction

**Evaluators (Core evaluation logic)**:

- [ ] T042 [P] [US1] Create base evaluator interface in src/jra/evaluators/base.py with abstract methods
- [ ] T043 [US1] Implement compliance checker in src/jra/evaluators/compliance.py for required field validation (depends on T029, T030)
- [ ] T044 [US1] Add field validation logic to compliance evaluator in src/jra/evaluators/compliance.py
- [ ] T045 [US1] Add workflow rule checking to compliance evaluator in src/jra/evaluators/compliance.py
- [ ] T046 [P] [US1] Write unit tests for compliance evaluator in tests/unit/test_evaluators.py::test_compliance_required_fields
- [ ] T047 [P] [US1] Write unit tests for field validation in tests/unit/test_evaluators.py::test_compliance_field_validations
- [ ] T048 [P] [US1] Write unit tests for workflow rules in tests/unit/test_evaluators.py::test_compliance_workflow_rules

**Formatters (Output generation)**:

- [ ] T049 [P] [US1] Implement JSON formatter in src/jra/formatters/json_formatter.py for machine-readable output
- [ ] T050 [P] [US1] Implement human-readable formatter in src/jra/formatters/human_formatter.py for terminal display
- [ ] T051 [P] [US1] Write unit tests for JSON formatter in tests/unit/test_formatters.py::test_json_formatter_compliance_report
- [ ] T052 [P] [US1] Write unit tests for human formatter in tests/unit/test_formatters.py::test_human_formatter_readability

**CLI Implementation**:

- [ ] T053 [US1] Implement evaluate command in src/jra/cli/evaluate.py with Click decorators and options (depends on T037-T050)
- [ ] T054 [US1] Wire up evaluation pipeline in evaluate command (parser → evaluator → formatter)
- [ ] T055 [US1] Add error handling and exit codes to evaluate command
- [ ] T056 [US1] Add --format, --timing, --debug options to evaluate command
- [ ] T057 [P] [US1] Write integration test for evaluate command with valid input in tests/integration/test_cli_evaluate.py::test_evaluate_valid_ticket
- [ ] T058 [P] [US1] Write integration test for evaluate command with violations in tests/integration/test_cli_evaluate.py::test_evaluate_ticket_with_violations
- [ ] T059 [P] [US1] Write integration test for error handling in tests/integration/test_cli_evaluate.py::test_evaluate_invalid_input

**Documentation and Polish**:

- [ ] T060 [P] [US1] Add docstrings to all public functions and classes in src/jra/ (US1 modules)
- [ ] T061 [US1] Run linters (Black, Flake8, mypy, isort) and fix all issues for US1 code
- [ ] T062 [US1] Verify test coverage ≥80% for US1 unit tests, ≥70% for US1 integration tests

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can evaluate a single Jira ticket and get a compliance report.

---

## Phase 4: User Story 2 - Detailed Quality Assessment (Priority: P2)

**Goal**: Add quality scoring across multiple dimensions (completeness, clarity, formatting, standards) with improvement recommendations

**Independent Test**: Evaluate multiple tickets, verify quality scores provided across dimensions, scores consistent for similar tickets, recommendations specific and actionable

### Tests for User Story 2 (TDD - Write these FIRST) ✅

- [ ] T063 [P] [US2] Write unit test for completeness evaluator in tests/unit/test_evaluators.py::test_completeness_scoring
- [ ] T064 [P] [US2] Write unit test for clarity evaluator in tests/unit/test_evaluators.py::test_clarity_readability_metrics
- [ ] T065 [P] [US2] Write unit test for quality aggregation in tests/unit/test_evaluators.py::test_quality_dimension_aggregation
- [ ] T066 [P] [US2] Write integration test for quality assessment in tests/integration/test_evaluation_flow.py::test_quality_scoring_consistency

### Implementation for User Story 2

**Models (Quality assessment models)**:

- [ ] T067 [P] [US2] Implement QualityAssessment model in src/jra/models/report.py with dimension scores and overall score
- [ ] T068 [P] [US2] Implement Recommendation model in src/jra/models/report.py with priority, category, title, description
- [ ] T069 [P] [US2] Update EvaluationReport model to include QualityAssessment and Recommendation list
- [ ] T070 [P] [US2] Write unit tests for quality models in tests/unit/test_models.py::test_quality_assessment_validation

**Evaluators (Quality scoring logic)**:

- [ ] T071 [P] [US2] Implement completeness evaluator in src/jra/evaluators/completeness.py for required field presence scoring
- [ ] T072 [P] [US2] Implement quality evaluator in src/jra/evaluators/quality.py for clarity, formatting, standards scoring
- [ ] T073 [US2] Add clarity metrics (readability, sentence analysis) to quality evaluator in src/jra/evaluators/quality.py
- [ ] T074 [US2] Add formatting metrics (markdown structure) to quality evaluator in src/jra/evaluators/quality.py
- [ ] T075 [US2] Add standards metrics (template adherence) to quality evaluator in src/jra/evaluators/quality.py
- [ ] T076 [US2] Implement recommender in src/jra/evaluators/recommender.py to generate actionable improvement suggestions
- [ ] T077 [P] [US2] Write unit tests for completeness evaluator in tests/unit/test_evaluators.py::test_completeness_field_presence
- [ ] T078 [P] [US2] Write unit tests for quality metrics in tests/unit/test_evaluators.py::test_quality_clarity_formatting_standards
- [ ] T079 [P] [US2] Write unit tests for recommender in tests/unit/test_evaluators.py::test_recommender_actionable_suggestions

**Update formatters for quality output**:

- [ ] T080 [US2] Update JSON formatter to include quality assessment and recommendations in src/jra/formatters/json_formatter.py
- [ ] T081 [US2] Update human formatter to display quality scores and recommendations in src/jra/formatters/human_formatter.py
- [ ] T082 [P] [US2] Write unit tests for quality output formatting in tests/unit/test_formatters.py::test_formatters_quality_display

**Update CLI for quality features**:

- [ ] T083 [US2] Integrate quality evaluators into evaluate command pipeline in src/jra/cli/evaluate.py
- [ ] T084 [P] [US2] Write integration test for quality assessment in tests/integration/test_cli_evaluate.py::test_evaluate_quality_scores
- [ ] T085 [P] [US2] Write integration test for recommendations in tests/integration/test_cli_evaluate.py::test_evaluate_recommendations

**Documentation and Polish**:

- [ ] T086 [P] [US2] Add docstrings to all US2 modules
- [ ] T087 [US2] Run linters and fix issues for US2 code
- [ ] T088 [US2] Verify test coverage for US2 modules

**Checkpoint**: User Story 1 AND 2 both work independently. Users can get detailed quality assessments with actionable recommendations.

---

## Phase 5: User Story 3 - Batch Evaluation and Reporting (Priority: P3)

**Goal**: Evaluate multiple tickets in single operation with aggregate report showing compliance trends and common violations

**Independent Test**: Provide 5-20 tickets, verify aggregate report shows overall compliance %, most common violations ranked by frequency, team-level trends

### Tests for User Story 3 (TDD - Write these FIRST) ✅

- [ ] T089 [P] [US3] Write unit test for batch aggregation in tests/unit/test_evaluators.py::test_batch_aggregate_metrics
- [ ] T090 [P] [US3] Write integration test for batch command in tests/integration/test_cli_batch.py::test_batch_command_basic_flow
- [ ] T091 [P] [US3] Write integration test for progress reporting in tests/integration/test_cli_batch.py::test_batch_progress_indicators

### Implementation for User Story 3

**Models (Batch reporting models)**:

- [ ] T092 [P] [US3] Create BatchReport model in src/jra/models/report.py with aggregate statistics
- [ ] T093 [P] [US3] Write unit tests for batch models in tests/unit/test_models.py::test_batch_report_validation

**Evaluators (Batch processing logic)**:

- [ ] T094 [US3] Implement batch aggregator in src/jra/evaluators/batch.py to collect and aggregate results
- [ ] T095 [US3] Add common violation detection logic to batch aggregator
- [ ] T096 [US3] Add quality distribution calculation to batch aggregator
- [ ] T097 [P] [US3] Write unit tests for batch aggregation in tests/unit/test_evaluators.py::test_batch_violation_frequency
- [ ] T098 [P] [US3] Write unit tests for quality distribution in tests/unit/test_evaluators.py::test_batch_quality_distribution

**Parsers (Batch input handling)**:

- [ ] T099 [US3] Add batch file parsing (JSON array and JSONL) to src/jra/parsers/jira_parser.py
- [ ] T100 [P] [US3] Write unit tests for batch parsing in tests/unit/test_parsers.py::test_batch_json_array_parsing

**Formatters (Batch output)**:

- [ ] T101 [P] [US3] Create batch formatter for JSON in src/jra/formatters/json_formatter.py
- [ ] T102 [P] [US3] Create batch formatter for human-readable in src/jra/formatters/human_formatter.py
- [ ] T103 [P] [US3] Write unit tests for batch formatters in tests/unit/test_formatters.py::test_batch_format_aggregate_stats

**CLI Implementation**:

- [ ] T104 [US3] Implement batch command in src/jra/cli/batch.py with Click decorators
- [ ] T105 [US3] Add progress bar using Click's progress utilities in src/jra/cli/batch.py
- [ ] T106 [US3] Add --continue-on-error flag handling in src/jra/cli/batch.py
- [ ] T107 [US3] Add --parallel option (set to 1 for MVP, prepare for future parallelization)
- [ ] T108 [P] [US3] Write integration test for batch with multiple tickets in tests/integration/test_cli_batch.py::test_batch_multiple_tickets
- [ ] T109 [P] [US3] Write integration test for continue-on-error in tests/integration/test_cli_batch.py::test_batch_continue_on_error

**Documentation and Polish**:

- [ ] T110 [P] [US3] Add docstrings to all US3 modules
- [ ] T111 [US3] Run linters and fix issues for US3 code
- [ ] T112 [US3] Verify test coverage for US3 modules

**Checkpoint**: All user stories 1, 2, AND 3 work independently. Teams can batch evaluate tickets and get aggregate insights.

---

## Phase 6: User Story 4 - Custom Guideline Configuration (Priority: P4)

**Goal**: Support custom evaluation rules beyond standard markdown (custom field validations, workflow states, organization-specific standards)

**Independent Test**: Create custom validation rules, apply during evaluation, verify tickets evaluated against both standard and custom rules

### Tests for User Story 4 (TDD - Write these FIRST) ✅

- [ ] T113 [P] [US4] Write unit test for custom rules parsing in tests/unit/test_parsers.py::test_custom_rules_parsing
- [ ] T114 [P] [US4] Write integration test for custom rules evaluation in tests/integration/test_evaluation_flow.py::test_custom_rules_application

### Implementation for User Story 4

**Models (Custom rules models)**:

- [ ] T115 [P] [US4] Extend ProcessGuidelines model to support custom rules in src/jra/models/guidelines.py
- [ ] T116 [P] [US4] Create CustomRule model in src/jra/models/guidelines.py with validation
- [ ] T117 [P] [US4] Write unit tests for custom rule models in tests/unit/test_models.py::test_custom_rule_validation

**Parsers (Custom rules parsing)**:

- [ ] T118 [US4] Add custom rules section parsing to markdown parser in src/jra/parsers/markdown_parser.py
- [ ] T119 [US4] Add custom rule validation to schema validator in src/jra/parsers/schema_validator.py
- [ ] T120 [P] [US4] Write unit tests for custom rules parsing in tests/unit/test_parsers.py::test_custom_rules_section_extraction

**Evaluators (Custom rules evaluation)**:

- [ ] T121 [US4] Extend compliance evaluator to apply custom rules in src/jra/evaluators/compliance.py
- [ ] T122 [US4] Add custom rule violation reporting in src/jra/evaluators/compliance.py
- [ ] T123 [P] [US4] Write unit tests for custom rule evaluation in tests/unit/test_evaluators.py::test_custom_rules_enforcement

**CLI and Configuration**:

- [ ] T124 [US4] Update configuration to support custom rule definitions in src/jra/utils/config.py
- [ ] T125 [P] [US4] Write integration test for custom rules via config in tests/integration/test_cli_evaluate.py::test_evaluate_custom_rules

**Documentation and Polish**:

- [ ] T126 [P] [US4] Add docstrings to all US4 modules
- [ ] T127 [US4] Run linters and fix issues for US4 code
- [ ] T128 [US4] Verify test coverage for US4 modules

**Checkpoint**: All user stories complete and independently functional. Full feature set delivered.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality assurance

- [ ] T129 [P] Create comprehensive README.md with installation, usage, examples, troubleshooting
- [ ] T130 [P] Create CONTRIBUTING.md with development setup, testing, PR guidelines
- [ ] T131 [P] Create sample guidelines in examples/guidelines/ for different team types
- [ ] T132 [P] Create sample tickets in examples/tickets/ (good and bad examples)
- [ ] T133 [P] Create CI/CD integration examples in examples/ci-cd/
- [ ] T134 [P] Add markdown formatter implementation in src/jra/formatters/markdown_formatter.py
- [ ] T135 [P] Write unit tests for markdown formatter in tests/unit/test_formatters.py::test_markdown_formatter
- [ ] T136 Code cleanup and refactoring for DRY principles across all modules
- [ ] T137 Performance optimization based on profiling (caching, lazy loading)
- [ ] T138 [P] Security audit with Bandit and address any critical/high vulnerabilities
- [ ] T139 [P] Run full test suite and ensure 80% unit coverage, 70% integration coverage
- [ ] T140 Generate API documentation from docstrings using Sphinx
- [ ] T141 Create quickstart validation script to verify examples work
- [ ] T142 Final linting pass (Black, Flake8, mypy, isort) with zero warnings
- [ ] T143 Update pyproject.toml with final version (1.0.0) and metadata

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1/US2 evaluation logic but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Extends US1 compliance logic but independently testable

### Within Each User Story

- Tests (TDD requirement) MUST be written and FAIL before implementation
- Models before services/evaluators
- Parsers before evaluators (evaluators depend on models from parsers)
- Evaluators before formatters
- Formatters before CLI commands
- CLI integration tests last within story
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T010)
- All Foundational tasks marked [P] can run in parallel within Phase 2 (T011-T020)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story:
  - All test tasks marked [P] can run in parallel
  - Model tasks marked [P] can run in parallel (T028-T036 for US1)
  - Parser tasks marked [P] can run in parallel after models (T039-T041 for US1)
  - Formatter tasks marked [P] can run in parallel (T049-T052 for US1)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task T023: Write contract test for Jira JSON input validation
Task T024: Write contract test for guidelines markdown parsing
Task T025: Write contract test for evaluation report JSON output
Task T026: Write integration test for evaluate command
Task T027: Write integration test for violation detection

# Launch all models for User Story 1 together:
Task T029: Implement JiraIssue model
Task T030: Implement ProcessGuidelines model
Task T031: Implement Violation model
Task T032: Implement ComplianceResult model
Task T033: Implement EvaluationReport model

# Launch all formatters for User Story 1 together:
Task T049: Implement JSON formatter
Task T050: Implement human-readable formatter
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T022) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T023-T062)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP Deliverable**: CLI tool that evaluates single Jira ticket against guidelines, produces compliance report with violations. Fully tested with ≥80% unit coverage.

### Incremental Delivery

1. Complete Setup + Foundational (Phases 1-2) → Foundation ready
2. Add User Story 1 (Phase 3) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Phase 4) → Test independently → Deploy/Demo (Quality assessment)
4. Add User Story 3 (Phase 5) → Test independently → Deploy/Demo (Batch processing)
5. Add User Story 4 (Phase 6) → Test independently → Deploy/Demo (Custom rules)
6. Polish (Phase 7) → Final release

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational is done:
   - Developer A: User Story 1 (T023-T062)
   - Developer B: User Story 2 (T063-T088)
   - Developer C: User Story 3 (T089-T112)
   - Developer D: User Story 4 (T113-T128)
3. Stories complete and integrate independently
4. Team collaborates on Polish (Phase 7)

---

## Notes

- **TDD Enforcement**: Per constitution, ALL tests MUST be written BEFORE implementation
- **[P] tasks**: Different files, no dependencies, can execute in parallel
- **[Story] label**: Maps task to specific user story for traceability (US1, US2, US3, US4)
- **File paths**: All tasks include exact file paths for clarity
- **Each user story**: Independently completable and testable
- **Test coverage**: Must maintain ≥80% unit, ≥70% integration per constitution
- **Quality gates**: Run linters (Black, Flake8, mypy, isort) after each story
- **Verify tests fail**: Before implementing, run tests to ensure they fail (red in TDD)
- **Commit frequency**: After each task or logical group
- **Stop at checkpoints**: Validate story independently before proceeding
- **Constitution compliance**: All code must pass linting with zero warnings

## Task Count Summary

- **Phase 1 (Setup)**: 10 tasks
- **Phase 2 (Foundational)**: 12 tasks (BLOCKING)
- **Phase 3 (User Story 1)**: 40 tasks (MVP - includes comprehensive tests)
- **Phase 4 (User Story 2)**: 26 tasks
- **Phase 5 (User Story 3)**: 24 tasks
- **Phase 6 (User Story 4)**: 16 tasks
- **Phase 7 (Polish)**: 15 tasks

**Total**: 143 tasks

**Parallel Opportunities**: 89 tasks marked [P] for parallel execution

**Test Tasks**: 42 dedicated test tasks (30% of total, ensuring TDD compliance)

**MVP Scope**: Phases 1-3 (62 tasks) delivers fully functional single-ticket evaluation with compliance reporting
