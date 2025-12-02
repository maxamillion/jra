"""Pytest configuration and shared fixtures."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture(autouse=True)
def disable_logging() -> None:
    """Disable logging during tests to prevent stderr contamination."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_jira_ticket(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample Jira ticket JSON."""
    ticket_path = fixtures_dir / "tickets" / "valid-story.json"
    if ticket_path.exists():
        with open(ticket_path) as f:
            return json.load(f)
    # Return minimal valid ticket if file doesn't exist yet
    return {
        "id": "12345",
        "key": "TEST-1",
        "fields": {
            "issuetype": {"name": "Story"},
            "status": {"name": "To Do"},
            "summary": "Sample user story",
            "description": "As a user, I want to test the system",
            "reporter": {"displayName": "Test User"},
            "created": "2025-01-01T00:00:00Z",
            "updated": "2025-01-01T00:00:00Z",
        },
    }


@pytest.fixture
def sample_guidelines(fixtures_dir: Path) -> str:
    """Load sample process guidelines markdown."""
    guidelines_path = fixtures_dir / "guidelines" / "basic-guidelines.md"
    if guidelines_path.exists():
        with open(guidelines_path) as f:
            return f.read()
    # Return minimal valid guidelines if file doesn't exist yet
    return """---
version: 1.0.0
last_updated: 2025-01-01
applies_to: [Story, Bug, Task]
---

# Process Guidelines

## Required Fields

All Stories must have:
- Summary (10-255 characters)
- Description (minimum 50 characters)
"""


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
