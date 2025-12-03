# Research: Jira Issue Evaluation AI Agent

**Phase**: 0 - Outline & Research
**Date**: 2025-11-26
**Purpose**: Resolve technical unknowns and establish best practices for implementation

## Technology Decisions

### 1. Python Version Selection

**Decision**: Python 3.11+

**Rationale**:
- **Performance**: 10-60% faster than 3.10 (relevant for document processing)
- **Type System**: Enhanced error messages in type checking
- **Pattern Matching**: Structural pattern matching simplifies parsing logic
- **Error Messages**: Better traceback information for debugging
- **LTS Support**: Supported until October 2027 (sufficient lifecycle)

**Alternatives Considered**:
- **Python 3.10**: More widely adopted, but slower and lacks pattern matching
- **Python 3.12**: Cutting edge features, but less stable, may have library compatibility issues
- **Python 3.9**: Too old, missing performance improvements and modern syntax

### 2. CLI Framework Selection

**Decision**: Click 8.1+

**Rationale**:
- **User Requirement**: Explicitly specified in user input
- **Rich Features**: Built-in support for progress bars, colors, parameter validation
- **Type Safety**: Integrates with type hints for parameter validation
- **Extensibility**: Plugin architecture for custom commands
- **Testing**: Excellent CliRunner for isolated CLI testing
- **Documentation**: Auto-generated help from docstrings
- **Composability**: Command groups for `evaluate` and `batch` subcommands

**Alternatives Considered**:
- **argparse**: Python stdlib, but verbose, poor UX, limited features
- **Typer**: Modern, type-hint based, but less mature ecosystem
- **Fire**: Google's library, too magical, poor validation control

### 3. Data Validation Framework

**Decision**: Pydantic v2.5+

**Rationale**:
- **Type Safety**: Runtime validation with static type hints
- **Performance**: v2 is Rust-based, 5-50x faster than v1
- **JSON Schema**: Auto-generates JSON schemas for contracts
- **Validation**: Rich validation with custom validators
- **Serialization**: Built-in JSON/dict serialization
- **Error Messages**: Clear, structured validation errors
- **IDE Support**: Excellent autocomplete and type checking

**Alternatives Considered**:
- **dataclasses**: Python stdlib, but no runtime validation
- **attrs**: Good validation, but less performant and verbose
- **marshmallow**: Mature, but slower and separate validation/serialization

### 4. Markdown Parsing

**Decision**: python-markdown 3.5+ with extensions

**Rationale**:
- **Extensible**: Plugin architecture for custom syntax
- **Standards**: GitHub Flavored Markdown (GFM) support via extensions
- **Parsing**: Access to parsed AST for structured analysis
- **Metadata**: Front matter support via extensions (for guideline versioning)
- **Testing**: Well-tested, stable library (2004-present)
- **Minimal**: Pure Python, no heavy dependencies

**Extensions Used**:
- `markdown.extensions.extra` - Tables, fenced code blocks, footnotes
- `markdown.extensions.codehilite` - Syntax highlighting
- `markdown.extensions.toc` - Table of contents extraction
- `pymdown-extensions` - GitHub Flavored Markdown features

**Alternatives Considered**:
- **mistune**: Faster, but less extensible for custom parsing
- **commonmark**: Strict CommonMark, but lacks GFM features
- **markdown-it-py**: Port of JS library, less Pythonic

### 5. Testing Strategy

**Decision**: pytest + pytest-cov + pytest-mock

**Rationale**:
- **pytest**: De facto Python testing standard, rich fixture system
- **pytest-cov**: Coverage reporting with branch coverage
- **pytest-mock**: Clean mocking interface built on unittest.mock
- **Fixtures**: Reusable test data in `conftest.py`
- **Parameterization**: Test multiple scenarios efficiently
- **Plugins**: Rich ecosystem for specialized testing needs

**Testing Approach**:
- **Unit Tests**: Each module tested in isolation with mocks
- **Integration Tests**: CLI tests using `CliRunner` with real fixtures
- **Contract Tests**: JSON schema validation for inputs/outputs
- **Snapshot Tests**: Optional `pytest-snapshot` for report regression testing

**Alternatives Considered**:
- **unittest**: Python stdlib, but verbose and less feature-rich
- **nose2**: Abandoned, community moved to pytest
- **tox**: Useful for multi-version testing, but overkill for initial development

### 6. Code Quality Tooling

**Decision**: Black + Flake8 + mypy + isort + Bandit

**Rationale**:

**Black (Code Formatting)**:
- Opinionated, zero-config formatter
- Eliminates style debates
- Compatible with Flake8

**Flake8 (Style Linting)**:
- PEP 8 compliance checking
- Complexity analysis (mccabe)
- Plugin ecosystem for custom rules

**mypy (Type Checking)**:
- Static type analysis
- Catches type errors before runtime
- Configurable strictness levels

**isort (Import Sorting)**:
- Automatic import organization
- Enforces consistent import structure
- Black-compatible configuration

**Bandit (Security Linting)**:
- Detects common security issues
- OWASP top 10 coverage
- Minimal false positives

**Alternatives Considered**:
- **Pylint**: More comprehensive, but slower and noisier
- **ruff**: New, fast Rust-based linter, but less mature
- **pytype**: Google's type checker, but slower than mypy

### 7. Configuration Management

**Decision**: TOML (pyproject.toml) + Python-dotenv

**Rationale**:
- **pyproject.toml**: Modern Python standard (PEP 518, 621, 631)
- **Centralized**: All tool configs in single file
- **Type Safety**: Structured format with schema validation
- **Environment**: python-dotenv for optional local overrides
- **No Dependencies**: TOML parsing in Python 3.11+ stdlib (`tomllib`)

**Configuration Hierarchy**:
1. Built-in defaults (in code)
2. `pyproject.toml` [tool.jra] section
3. `.env` file (optional, for local dev)
4. Environment variables (runtime overrides)
5. CLI flags (highest priority)

**Alternatives Considered**:
- **YAML**: More features, but requires PyYAML dependency
- **JSON**: No comments, less human-friendly for config
- **INI**: Limited structure, deprecated pattern

### 8. Performance Optimization Techniques

**Decision**: Caching + Lazy Loading + Generators

**Techniques**:

**Guideline Caching**:
- `functools.lru_cache` for parsed guidelines
- Cache key: file path + mtime hash
- Invalidate on file change detection

**Lazy Loading**:
- Parse guidelines only when needed
- Defer ticket loading until evaluation
- Stream large batch files vs loading all into memory

**Generator Patterns**:
- Use generators for batch processing (`yield` instead of lists)
- Process tickets one at a time, don't accumulate in memory
- Output streaming for large reports

**Profiling**:
- `cProfile` for identifying hot paths
- `memory_profiler` for memory usage analysis
- `--timing` flag to expose performance metrics to users

**Alternatives Considered**:
- **External Caching**: Redis/memcached overkill for CLI tool
- **Multiprocessing**: Adds complexity, limited by Python GIL for document processing
- **Async/await**: No I/O-bound operations benefit, adds complexity

### 9. Error Handling Strategy

**Decision**: Custom Exception Hierarchy + Rich Error Context

**Exception Design**:
```
JRAException (base)
├── ParseError
│   ├── JiraParseError
│   └── GuidelineParseError
├── ValidationError
│   ├── SchemaValidationError
│   └── ConfigValidationError
├── EvaluationError
│   ├── ComplianceCheckError
│   └── QualityAssessmentError
└── OutputError
    ├── FormattingError
    └── IOError
```

**Error Context**:
- Include source location (file, line number)
- Attach relevant data (ticket ID, guideline section)
- Suggest remediation actions
- Exit codes for automation (0: success, 1: usage error, 2: validation error, 3: evaluation error)

**Alternatives Considered**:
- **Result Types**: Rust-style Result<T, E>, but not Pythonic
- **Exception-less**: Return codes, but loses stack traces and context

### 10. Minimal Dependencies Philosophy

**Decision**: Core dependencies only, prefer stdlib

**Core Dependencies** (6 total):
1. **click**: CLI framework (user requirement)
2. **pydantic**: Data validation and type safety
3. **python-markdown**: Markdown parsing (with extensions)
4. **PyYAML**: YAML support (if guidelines support YAML front matter)
5. **python-dotenv**: Environment variable loading (optional)
6. **typing-extensions**: Backport for older Python type features

**Dev Dependencies** (testing/quality):
- pytest, pytest-cov, pytest-mock
- black, flake8, mypy, isort, bandit
- safety (dependency security scanning)

**Rationale**:
- **Security**: Fewer deps = smaller attack surface
- **Maintainability**: Less dependency churn and breakage
- **Performance**: No bloat, faster installation
- **Reliability**: Fewer transitive dependency conflicts
- **Constitution**: Aligns with "minimal dependencies" constraint

**Rejected Dependencies**:
- **Rich**: Beautiful terminal output, but adds complexity for minimal benefit
- **Requests**: HTTP library not needed (offline tool)
- **SQLAlchemy**: No database requirements
- **Pandas**: Overkill for simple data structures
- **NumPy/SciPy**: No numerical computing requirements

## Best Practices Research

### Python Idioms for CLI Tools

**Package Structure**:
- `src/` layout to avoid import issues
- `__main__.py` for `python -m jra` entry point
- Entry point in `pyproject.toml` for `jra` command installation

**CLI Patterns**:
- Click command groups for subcommands
- `--help` text from docstrings
- `--version` from package metadata
- Progress feedback for operations >2 seconds
- Color support detection (respect `NO_COLOR` env var)

**Error Handling**:
- Catch exceptions at CLI boundary
- User-friendly error messages to stderr
- Stack traces only with `--debug` flag
- Non-zero exit codes for automation

### Jira API Data Structures

**Research**: Jira REST API v3 response format

**Key Ticket Fields**:
- `id`, `key` (e.g., PROJ-123)
- `fields.issuetype` (Story, Bug, Epic, Task)
- `fields.status` (To Do, In Progress, Done)
- `fields.summary` (title/short description)
- `fields.description` (detailed description, can be ADF or markdown)
- `fields.priority`, `fields.labels`, `fields.components`
- `fields.assignee`, `fields.reporter`, `fields.created`, `fields.updated`
- `fields.customfield_*` (organization-specific fields)

**Jira Description Formats**:
- **ADF** (Atlassian Document Format): JSON-based rich text (Jira Cloud default)
- **Wiki Markup**: Legacy format (Jira Server)
- **Markdown**: Some Jira instances support markdown

**Parsing Strategy**:
- Detect format from content structure
- Convert ADF to plain text for analysis
- Support markdown natively
- Extract text from wiki markup

### Markdown Guidelines Structure

**Best Practices from Research**:

**Front Matter** (optional YAML):
```yaml
---
version: 1.2.0
last_updated: 2025-11-26
applies_to: [Story, Bug, Task]
---
```

**Guideline Sections**:
- **Required Fields**: List of mandatory Jira fields per issue type
- **Field Validations**: Rules for field content (length, format, vocabulary)
- **Workflow Rules**: Allowed state transitions and prerequisites
- **Quality Criteria**: Scoring rubrics for completeness, clarity, formatting
- **Templates**: Examples of well-formed tickets

**Parsing Strategy**:
- Extract headings as section identifiers
- Parse lists/tables as structured rules
- Support code blocks for examples
- Links to reference additional guidelines

### Quality Assessment Heuristics

**Completeness Scoring**:
- Required fields present: 40%
- Required fields non-empty: 30%
- Optional fields present: 20%
- Attachments/links present: 10%

**Clarity Scoring**:
- Sentence count (too short = unclear): 20%
- Average sentence length (too long = complex): 20%
- Passive voice detection (prefer active): 15%
- Jargon/acronym ratio: 15%
- Readability score (Flesch-Kincaid): 30%

**Formatting Scoring**:
- Markdown structure (headings, lists): 30%
- Code blocks for technical content: 20%
- Acceptance criteria formatting: 30%
- Spelling/grammar: 20%

**Standards Adherence Scoring**:
- Follows guideline templates: 40%
- Uses standard vocabulary: 30%
- Follows naming conventions: 20%
- Links to requirements: 10%

## Implementation Risks & Mitigations

### Risk 1: Guideline Ambiguity

**Risk**: Process guidelines may have vague or contradictory requirements

**Mitigation**:
- Validate guideline structure during parsing
- Report ambiguous rules to user
- Provide guideline linting/validation command
- Support strict mode (fails on ambiguity) vs lenient mode (warnings)

### Risk 2: Jira Format Variations

**Risk**: Different Jira instances use different formats (Cloud, Server, Data Center)

**Mitigation**:
- Support multiple description formats (ADF, Markdown, Wiki)
- Fallback to plain text extraction
- Document supported Jira versions in README
- Provide format detection with user override

### Risk 3: Performance with Large Tickets

**Risk**: Tickets with hundreds of comments may exceed performance targets

**Mitigation**:
- Lazy evaluation (skip comment analysis unless required by guidelines)
- Configurable comment limit (default: analyze first 50 comments)
- Progress reporting for slow operations
- Timeout handling with partial results

### Risk 4: Subjective Quality Metrics

**Risk**: "Clarity" and "quality" are subjective, users may disagree with scores

**Mitigation**:
- Document scoring algorithms transparently
- Allow custom scoring weights in config
- Provide score breakdown (not just final number)
- Include example tickets with expected scores
- Make recommendations primary output, scores secondary

## References

- [Click Documentation](https://click.palletsprojects.com/) - CLI framework
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation
- [Python-Markdown Documentation](https://python-markdown.github.io/) - Markdown parsing
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) - API reference
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [PEP 8](https://peps.python.org/pep-0008/) - Python style guide
- [PEP 257](https://peps.python.org/pep-0257/) - Docstring conventions
- [Semantic Versioning](https://semver.org/) - Version numbering
