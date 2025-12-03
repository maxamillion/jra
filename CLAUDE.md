# jra Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-02

---
**🚨 MANDATORY REQUIREMENTS - NO EXCEPTIONS 🚨**

1. **ALWAYS use the `.venv` virtual environment** - Check with `which python` before ANY command
2. **ALWAYS use `uv pip` instead of `pip`** - NEVER use pip, pip3, or python -m pip directly
3. **ALWAYS activate virtualenv first** - Run `source .venv/bin/activate` before any Python work
4. **VERIFY virtualenv is active** - Ensure shell prompt shows `(.venv)` prefix

If virtualenv is not active or uv is not being used, STOP and activate it first.
---

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

**🚨 ABSOLUTE REQUIREMENTS - ZERO EXCEPTIONS 🚨**

This project has **MANDATORY** virtualenv and uv requirements. Every single Python operation must follow these rules:

### Pre-Flight Checklist (Run BEFORE every operation)

```bash
# 1. Check if virtualenv is active
which python
# MUST show: /home/admiller/src/jra/.venv/bin/python
# If not, STOP and activate virtualenv

# 2. Activate virtualenv if needed
source .venv/bin/activate

# 3. Verify activation succeeded
echo $VIRTUAL_ENV
# MUST show: /home/admiller/src/jra/.venv
```

### Initial Setup

```bash
# Install uv if not already available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment using uv (Python 3.11+)
uv venv --python 3.11

# Activate virtual environment - MANDATORY for all subsequent commands
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows

# Install dependencies using uv (NOT pip!)
uv pip install -e ".[dev]"
```

### Daily Development Workflow - MANDATORY PATTERN

```bash
# ======================================
# STEP 1: ALWAYS ACTIVATE FIRST
# ======================================
source .venv/bin/activate

# ======================================
# STEP 2: VERIFY ACTIVATION
# ======================================
which python  # MUST show .venv/bin/python

# ======================================
# STEP 3: Use uv pip for ALL operations
# ======================================

# Add new dependencies using uv (NEVER use pip!)
uv pip install <package-name>

# Update dependencies
uv pip install --upgrade <package-name>

# Sync dependencies from pyproject.toml
uv pip sync

# Install in development mode
uv pip install -e ".[dev]"

# ======================================
# STEP 4: Deactivate when done
# ======================================
deactivate
```

### Dependency Management Rules - ABSOLUTE

1. **ALWAYS use `uv pip` instead of `pip`** - uv is significantly faster and more reliable
2. **NEVER EVER use `pip`, `pip3`, or `python -m pip` directly** - all package operations MUST go through `uv pip`
3. **ALWAYS activate virtualenv FIRST** - Check with `which python` before ANY command
4. **VERIFY before executing** - Ensure `which python` shows `.venv/bin/python`
5. **Keep pyproject.toml as source of truth** - manually edit dependencies there, then sync
6. **Lock dependencies with uv** - uv automatically maintains uv.lock for reproducible builds
7. **Use extras for optional dependencies** - separate dev, test, and optional features

### ❌ FORBIDDEN COMMANDS ❌

```bash
# NEVER use these commands:
pip install <package>           # ❌ FORBIDDEN - use: uv pip install
pip3 install <package>          # ❌ FORBIDDEN - use: uv pip install
python -m pip install <package> # ❌ FORBIDDEN - use: uv pip install
sudo pip install <package>      # ❌ FORBIDDEN - NEVER install globally

# Also forbidden without virtualenv active:
pytest                          # ❌ Must activate .venv first
python <script>                 # ❌ Must activate .venv first
mypy <path>                     # ❌ Must activate .venv first
ruff <command>                  # ❌ Must activate .venv first
```

### ✅ CORRECT PATTERNS ✅

```bash
# ALWAYS follow this pattern:
source .venv/bin/activate       # ✅ Step 1: Activate
which python                    # ✅ Step 2: Verify
uv pip install <package>        # ✅ Step 3: Use uv pip
pytest                          # ✅ Step 4: Run commands
deactivate                      # ✅ Step 5: Deactivate when done
```

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
# ALWAYS activate virtualenv first!
source .venv/bin/activate

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
# ALWAYS activate virtualenv first!
source .venv/bin/activate

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
# ALWAYS activate virtualenv first!
source .venv/bin/activate

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
# ALWAYS activate virtualenv first!
source .venv/bin/activate

# Run test suite
pytest

# Run with coverage
pytest --cov=src/jra --cov-report=html

# Run specific test
pytest tests/test_cli.py::test_main_command
```

### Building and Distribution

```bash
# ALWAYS activate virtualenv first!
source .venv/bin/activate

# Build package
python -m build

# Install locally for testing
uv pip install -e .
```

## Git Workflow

**🚨 MANDATORY: Activate virtualenv BEFORE any git workflow commands 🚨**

```bash
# STEP 1: ALWAYS activate virtualenv first
source .venv/bin/activate

# STEP 2: Verify virtualenv is active
which python  # MUST show: /home/admiller/src/jra/.venv/bin/python

# STEP 3: Run quality checks
ruff check . && mypy src/ && pytest

# STEP 4: Stage and commit changes
git add <files>
git commit -m "descriptive message"
```

**Git Workflow Rules**:

1. **ALWAYS activate virtualenv FIRST** - Verify with `which python` showing `.venv/bin/python`
2. **NEVER skip quality checks** - Run `ruff check . && mypy src/ && pytest` before EVERY commit
3. **Use uv pip exclusively** - NEVER use pip for any dependency changes
4. **Write descriptive commit messages** - Follow conventional commits format
5. **Keep commits focused** - One logical change per commit
6. **Never commit virtualenv or cache files** - Ensure `.gitignore` is comprehensive
7. **Verify virtualenv state** - Check `which python` shows correct path before pushing

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

## Quick Reference Summary

### Every Command Must Follow This Pattern

```bash
# 1️⃣ ACTIVATE (required for ALL operations)
source .venv/bin/activate

# 2️⃣ VERIFY (check before proceeding)
which python  # Must show: /home/admiller/src/jra/.venv/bin/python

# 3️⃣ EXECUTE (use uv pip for package operations)
uv pip install <package>  # ✅ CORRECT
# pip install <package>   # ❌ FORBIDDEN

# 4️⃣ RUN (Python commands)
pytest                     # ✅ Now safe to run
ruff check .              # ✅ Now safe to run
mypy src/                 # ✅ Now safe to run
```

### Universal Rules (No Exceptions)

| Rule | Command | Status |
|------|---------|--------|
| Use uv pip | `uv pip install` | ✅ REQUIRED |
| Never use pip | `pip install` | ❌ FORBIDDEN |
| Activate first | `source .venv/bin/activate` | ✅ REQUIRED |
| Verify activation | `which python` | ✅ REQUIRED |
| Check virtualenv | Must show `.venv/bin/python` | ✅ REQUIRED |

### Common Mistakes to Avoid

❌ **WRONG**: Running commands without virtualenv
```bash
pytest                    # ❌ NO! Virtualenv not active
pip install requests      # ❌ NO! Using pip instead of uv pip
```

✅ **CORRECT**: Always activate first
```bash
source .venv/bin/activate # ✅ Activate first
which python              # ✅ Verify
uv pip install requests   # ✅ Use uv pip
pytest                    # ✅ Now safe to run
```

## Recent Changes

- 001-jira-evaluation: Added Python 3.11+ + Click (CLI), Pydantic (validation), python-markdown (parsing), PyYAML (config)
- 2025-12-02: Enhanced virtualenv and uv requirements with explicit enforcement and forbidden patterns

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
