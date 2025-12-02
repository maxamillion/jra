"""Pydantic models for Jira issue representation.

Models for parsing and validating Jira API JSON responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    """Jira user model."""

    display_name: str = Field(..., description="User's display name")
    email_address: Optional[str] = Field(None, description="User's email address")

    class Config:
        """Pydantic configuration."""

        frozen = False


class Comment(BaseModel):
    """Jira comment model."""

    author: User = Field(..., description="Comment author")
    body: str = Field(..., description="Comment text")
    created: datetime = Field(..., description="Comment creation timestamp")

    class Config:
        """Pydantic configuration."""

        frozen = False


class Attachment(BaseModel):
    """Jira attachment model."""

    filename: str = Field(..., description="Attachment filename")
    mime_type: Optional[str] = Field(None, description="MIME type")
    size: Optional[int] = Field(None, description="File size in bytes")
    created: Optional[datetime] = Field(None, description="Upload timestamp")

    class Config:
        """Pydantic configuration."""

        frozen = False


class IssueType(BaseModel):
    """Jira issue type model."""

    name: str = Field(..., description="Issue type name (Story, Bug, Task, Epic)")
    subtask: bool = Field(default=False, description="Whether this is a subtask")

    class Config:
        """Pydantic configuration."""

        frozen = False


class Priority(BaseModel):
    """Jira priority model."""

    name: str = Field(..., description="Priority name (Blocker, Critical, Major, Minor, Trivial)")

    class Config:
        """Pydantic configuration."""

        frozen = False


class Status(BaseModel):
    """Jira status model."""

    name: str = Field(..., description="Status name (To Do, In Progress, Done, etc.)")

    class Config:
        """Pydantic configuration."""

        frozen = False


class Project(BaseModel):
    """Jira project model."""

    key: str = Field(..., description="Project key")
    name: Optional[str] = Field(None, description="Project name")

    class Config:
        """Pydantic configuration."""

        frozen = False


class Component(BaseModel):
    """Jira component model."""

    name: str = Field(..., description="Component name")

    class Config:
        """Pydantic configuration."""

        frozen = False


class Subtask(BaseModel):
    """Jira subtask reference model."""

    key: str = Field(..., description="Subtask key")
    summary: Optional[str] = Field(None, description="Subtask summary")

    class Config:
        """Pydantic configuration."""

        frozen = False


class JiraIssue(BaseModel):
    """Complete Jira issue model.

    Represents a Jira ticket with all standard and custom fields.
    """

    # Required fields
    id: str = Field(..., description="Issue ID")
    key: str = Field(..., description="Issue key (e.g., PROJ-123)")
    summary: str = Field(..., description="Issue summary/title")
    issue_type: IssueType = Field(..., description="Issue type")
    status: Status = Field(..., description="Current status")
    project: Project = Field(..., description="Parent project")
    reporter: User = Field(..., description="User who created the issue")

    # Common optional fields
    description: Optional[str] = Field(None, description="Issue description")
    assignee: Optional[User] = Field(None, description="Assigned user")
    priority: Optional[Priority] = Field(None, description="Issue priority")
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    updated: Optional[datetime] = Field(None, description="Last update timestamp")
    duedate: Optional[str] = Field(None, description="Due date (ISO format)")

    # Collections
    labels: List[str] = Field(default_factory=list, description="Issue labels")
    components: List[Component] = Field(default_factory=list, description="Issue components")
    comments: List[Comment] = Field(default_factory=list, description="Issue comments")
    attachments: List[Attachment] = Field(default_factory=list, description="Issue attachments")
    subtasks: List[Subtask] = Field(default_factory=list, description="Subtasks")

    # Custom fields (preserved for extensibility)
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom field values")

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, v: str) -> str:
        """Validate summary is not empty."""
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        return v.strip()

    @field_validator("key")
    @classmethod
    def key_format(cls, v: str) -> str:
        """Validate key format (PROJECT-NUMBER)."""
        if not v or "-" not in v:
            raise ValueError("Issue key must be in format PROJECT-NUMBER")
        return v

    class Config:
        """Pydantic configuration."""

        frozen = False
        validate_assignment = True

    def get_issue_type_name(self) -> str:
        """Get issue type name as string.

        Returns:
            Issue type name (Story, Bug, Task, Epic, etc.)
        """
        return self.issue_type.name

    def get_status_name(self) -> str:
        """Get status name as string.

        Returns:
            Status name (To Do, In Progress, Done, etc.)
        """
        return self.status.name

    def get_priority_name(self) -> Optional[str]:
        """Get priority name as string.

        Returns:
            Priority name if set, None otherwise
        """
        return self.priority.name if self.priority else None

    def has_description(self) -> bool:
        """Check if issue has a description.

        Returns:
            True if description exists and is not empty
        """
        return bool(self.description and self.description.strip())

    def has_assignee(self) -> bool:
        """Check if issue has an assignee.

        Returns:
            True if assignee is set
        """
        return self.assignee is not None

    def comment_count(self) -> int:
        """Get number of comments.

        Returns:
            Count of comments
        """
        return len(self.comments)

    def attachment_count(self) -> int:
        """Get number of attachments.

        Returns:
            Count of attachments
        """
        return len(self.attachments)

    def has_label(self, label: str) -> bool:
        """Check if issue has a specific label.

        Args:
            label: Label to check for

        Returns:
            True if label exists
        """
        return label in self.labels

    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """Get custom field value.

        Args:
            field_name: Custom field name (e.g., "customfield_10001")
            default: Default value if field doesn't exist

        Returns:
            Custom field value or default
        """
        return self.custom_fields.get(field_name, default)
