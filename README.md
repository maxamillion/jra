# Jira Review Agent (jra)

AI-powered CLI tool that evaluates Jira issue tickets against team process guidelines.

## Features

- ✅ **Single Ticket Evaluation**: Evaluate individual Jira tickets against process guidelines
- ✅ **Quality Assessment**: Multi-dimensional scoring (completeness, clarity, formatting, standards)
- ✅ **Batch Processing**: Evaluate multiple tickets with aggregate reporting
- ✅ **Custom Rules**: Define organization-specific validation rules
- ✅ **Multiple Output Formats**: JSON, human-readable, and markdown reports
- ✅ **Offline Capable**: No external dependencies, works offline

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Install from source

```bash
git clone https://github.com/your-org/jra.git
cd jra
pip install -e .
```

### Install development dependencies

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Prepare Your Inputs

You need two files:
- **Jira Ticket** (JSON format from Jira API)
- **Process Guidelines** (Markdown format)

### 2. Evaluate a Ticket

```bash
jra evaluate ticket.json guidelines.md
```

### 3. View the Report

```
Jira Issue Evaluation Report
=============================

Ticket: PROJ-123
Overall Status: PASS ✓

Quality Assessment
------------------
Overall Score: 88/100 (Good)
```

## Usage

### Evaluate Command

```bash
# Basic evaluation
jra evaluate ticket.json guidelines.md

# JSON output for automation
jra evaluate ticket.json guidelines.md --format json > report.json

# With timing metrics
jra evaluate ticket.json guidelines.md --timing

# Strict mode (warnings are errors)
jra evaluate ticket.json guidelines.md --strict
```

### Batch Command

```bash
# Evaluate multiple tickets
jra batch tickets.json guidelines.md

# With progress bar
jra batch tickets.json guidelines.md --progress

# Parallel processing
jra batch tickets.json guidelines.md --parallel 4
```

## Configuration

Create `~/.jra/config.toml`:

```toml
[evaluation]
strict_mode = false
default_format = "human"

[quality.thresholds]
excellent = 90.0
good = 75.0
acceptable = 60.0
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/jra.git
cd jra

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=jra --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

## Project Structure

```
jra/
├── src/jra/           # Main package
│   ├── cli/           # Command-line interface
│   ├── models/        # Pydantic data models
│   ├── parsers/       # Input parsing (Jira JSON, Guidelines markdown)
│   ├── evaluators/    # Evaluation logic
│   ├── formatters/    # Output formatting
│   └── utils/         # Utilities (config, logging, timing)
├── tests/             # Test suite
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── fixtures/      # Test data
├── pyproject.toml     # Project configuration
└── README.md          # This file
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/your-org/jra/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/jra/discussions)
