# jra Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-02

## Active Technologies

- **Python 3.11+**: Modern Python with latest features including structural pattern matching, improved type hints, and enhanced error messages
- **Click**: Command-line interface framework with composable commands and type-safe parameter handling
- **Pydantic**: Data validation using Python type annotations with automatic validation and serialization
- **python-markdown**: Markdown parsing and rendering for documentation and content processing
- **PyYAML**: YAML configuration file parsing with safe loading practices
- **uv**: Ultra-fast Python package installer and virtualenv manager (REQUIRED for all virtualenv operations)

## Project Structure

```text
jra/
├── src/                    # Source code directory
│   └── jra/               # Main package
├── tests/                 # Test directory (mirrors src/ structure)
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock               # Locked dependencies (managed by uv)
└── .python-version       # Python version specification for uv
```

## Python Virtual Environment Management

**CRITICAL**: This project MUST always use virtual environments managed by `uv`. Never install packages globally or use other virtualenv tools.

### Initial Setup

```bash
# Install uv if not already available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment using uv (Python 3.11+)
uv venv --python 3.11

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows

# Install dependencies using uv
uv pip install -e ".[dev]"
```

### Daily Development Workflow

```bash
# ALWAYS activate virtualenv before any Python work
source .venv/bin/activate

# Add new dependencies using uv (not pip!)
uv pip install <package-name>

# Update dependencies
uv pip install --upgrade <package-name>

# Sync dependencies from pyproject.toml
uv pip sync

# Deactivate when done
deactivate
```

### Dependency Management Rules

1. **ALWAYS use `uv pip` instead of `pip`** - uv is significantly faster and more reliable
2. **NEVER use `pip` directly** - all package operations must go through uv
3. **Keep pyproject.toml as source of truth** - manually edit dependencies there, then sync
4. **Lock dependencies with uv** - uv automatically maintains uv.lock for reproducible builds
5. **Use extras for optional dependencies** - separate dev, test, and optional features

## Python Best Practices

### Code Style and Standards

1. **PEP 8 Compliance**: Follow Python Enhancement Proposal 8 for code style
   - 4 spaces for indentation (never tabs)
   - Max line length: 100 characters (not the old 79)
   - Use blank lines to separate logical sections
   - Import organization: stdlib → third-party → local

2. **Type Hints**: Use comprehensive type annotations (Python 3.11+ syntax)
   ```python
   from typing import TypeAlias

   UserId: TypeAlias = str

   def process_user(user_id: UserId, name: str) -> dict[str, str | int]:
       return {"id": user_id, "name": name, "count": 1}
   ```

3. **Naming Conventions**:
   - `snake_case` for functions, variables, and module names
   - `PascalCase` for class names
   - `SCREAMING_SNAKE_CASE` for constants
   - Prefix private members with single underscore: `_internal_method`
   - Avoid double underscore prefix unless you need name mangling

4. **Docstrings**: Use Google-style docstrings for all public APIs
   ```python
   def calculate_total(items: list[float], tax_rate: float = 0.0) -> float:
       """Calculate total price including tax.

       Args:
           items: List of item prices
           tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

       Returns:
           Total price with tax applied

       Raises:
           ValueError: If tax_rate is negative
       """
       if tax_rate < 0:
           raise ValueError("Tax rate cannot be negative")
       subtotal = sum(items)
       return subtotal * (1 + tax_rate)
   ```

5. **Error Handling**:
   - Use specific exception types, not bare `except:`
   - Fail fast with meaningful error messages
   - Use custom exceptions for domain-specific errors
   - Always clean up resources with context managers

6. **Modern Python Features** (3.11+):
   - Use structural pattern matching (`match`/`case`) for complex conditionals
   - Leverage improved error messages and tracebacks
   - Use `Self` type for fluent interfaces
   - Apply `ExceptionGroup` for multiple concurrent errors

### Code Organization

1. **Module Structure**: One class per file for complex classes, group related functions
2. **Separation of Concerns**: Keep business logic separate from I/O and presentation
3. **Dependency Injection**: Pass dependencies explicitly rather than using globals
4. **Single Responsibility**: Each function/class should have one clear purpose
5. **DRY Principle**: Extract common functionality, avoid duplication

### Testing Practices

```bash
# Run all tests with pytest
pytest

# Run with coverage report
pytest --cov=src/jra --cov-report=term-missing

# Run specific test file
pytest tests/test_specific.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_user"
```

**Testing Standards**:
- Minimum 80% code coverage for new code
- Use fixtures for test setup and teardown
- Mock external dependencies (APIs, databases, file system)
- Test edge cases and error conditions
- Keep tests fast (< 1ms for unit tests)
- Use parametrize for testing multiple inputs

### Code Quality Tools

```bash
# Run ruff for linting and formatting
ruff check .                    # Check for issues
ruff check --fix .             # Auto-fix issues
ruff format .                   # Format code

# Type checking with mypy
mypy src/

# Security scanning
bandit -r src/
```

**Quality Standards**:
- Zero ruff violations before commit
- All type hints must pass mypy strict mode
- No security issues from bandit
- All tests must pass
- Code coverage must not decrease

## Development Commands

### Setup and Environment

```bash
# Create fresh virtualenv with uv
uv venv --python 3.11

# Activate virtualenv (REQUIRED before any Python work)
source .venv/bin/activate

# Install project in development mode
uv pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code automatically
ruff format .

# Check and fix linting issues
ruff check --fix .

# Type check
mypy src/

# Run all quality checks
ruff check . && mypy src/ && pytest
```

### Testing

```bash
# Run test suite
pytest

# Run with coverage
pytest --cov=src/jra --cov-report=html

# Run specific test
pytest tests/test_cli.py::test_main_command
```

### Building and Distribution

```bash
# Build package
python -m build

# Install locally for testing
uv pip install -e .
```

## Git Workflow

1. **Always work in a virtualenv** - Verify with `which python` showing `.venv/bin/python`
2. **Run quality checks before commit** - `ruff check . && mypy src/ && pytest`
3. **Write descriptive commit messages** - Follow conventional commits format
4. **Keep commits focused** - One logical change per commit
5. **Never commit virtualenv or cache files** - Ensure `.gitignore` is comprehensive

## Performance Considerations

1. **Use `uv` for all package operations** - 10-100x faster than pip
2. **Lazy imports** - Import heavy modules only when needed
3. **Generator expressions** - Use generators for large datasets instead of lists
4. **Profile before optimizing** - Use `cProfile` or `line_profiler` to identify bottlenecks
5. **Cache expensive operations** - Use `@functools.lru_cache` for pure functions

## Security Best Practices

1. **Input validation** - Use Pydantic models to validate all external input
2. **Safe YAML loading** - Always use `yaml.safe_load()`, never `yaml.load()`
3. **Dependency scanning** - Regularly run `uv pip audit` to check for vulnerabilities
4. **Secrets management** - Never commit secrets; use environment variables or secret managers
5. **Least privilege** - Request minimum necessary permissions for file/network operations

## Recent Changes

- 001-jira-evaluation: Added Python 3.11+ + Click (CLI), Pydantic (validation), python-markdown (parsing), PyYAML (config)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
