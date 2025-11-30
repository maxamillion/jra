"""Jira JSON parser implementation.

Parses Jira API JSON responses into JiraIssue models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from jra.models.jira import (
    Attachment,
    Comment,
    Component,
    IssueType,
    JiraIssue,
    Priority,
    Project,
    Status,
    Subtask,
    User,
)
from jra.utils.exceptions import JiraParseError


class JiraParser:
    """Parser for Jira API JSON responses.

    Converts raw Jira JSON into validated JiraIssue models.
    """

    def parse(self, data: Dict[str, Any]) -> JiraIssue:
        """Parse Jira JSON data into JiraIssue model.

        Args:
            data: Raw Jira JSON data from API

        Returns:
            Parsed and validated JiraIssue instance

        Raises:
            JiraParseError: If JSON structure is invalid or required fields missing
        """
        try:
            # Validate basic structure
            if not isinstance(data, dict):
                raise JiraParseError("Invalid JSON structure: expected object")

            if "fields" not in data:
                raise JiraParseError("Missing 'fields' in Jira JSON")

            fields = data["fields"]

            # Extract required fields
            issue_id = data.get("id")
            if not issue_id:
                raise JiraParseError("Missing required field: id")

            key = data.get("key")
            if not key:
                raise JiraParseError("Missing required field: key")

            summary = fields.get("summary")
            if not summary:
                raise JiraParseError("Missing required field: summary")

            # Parse nested objects
            issue_type = self._parse_issue_type(fields.get("issuetype"))
            status = self._parse_status(fields.get("status"))
            project = self._parse_project(fields.get("project"))
            reporter = self._parse_user(fields.get("reporter"), "reporter")

            # Parse optional fields
            description = fields.get("description")
            assignee = self._parse_user(fields.get("assignee"), "assignee") if fields.get("assignee") else None
            priority = self._parse_priority(fields.get("priority")) if fields.get("priority") else None

            # Parse timestamps
            created = self._parse_datetime(fields.get("created"))
            updated = self._parse_datetime(fields.get("updated"))
            duedate = fields.get("duedate")

            # Parse collections
            labels = fields.get("labels", [])
            components = self._parse_components(fields.get("components", []))
            comments = self._parse_comments(fields.get("comment", {}))
            attachments = self._parse_attachments(fields.get("attachment", []))
            subtasks = self._parse_subtasks(fields.get("subtasks", []))

            # Extract custom fields
            custom_fields = self._extract_custom_fields(fields)

            # Create and return JiraIssue
            return JiraIssue(
                id=issue_id,
                key=key,
                summary=summary,
                issue_type=issue_type,
                status=status,
                project=project,
                reporter=reporter,
                description=description,
                assignee=assignee,
                priority=priority,
                created=created,
                updated=updated,
                duedate=duedate,
                labels=labels,
                components=components,
                comments=comments,
                attachments=attachments,
                subtasks=subtasks,
                custom_fields=custom_fields,
            )

        except JiraParseError:
            raise
        except Exception as e:
            raise JiraParseError(f"Failed to parse Jira JSON: {str(e)}") from e

    def _parse_issue_type(self, data: Optional[Dict[str, Any]]) -> IssueType:
        """Parse issue type from JSON."""
        if not data:
            raise JiraParseError("Missing required field: issuetype")

        name = data.get("name")
        if not name:
            raise JiraParseError("Issue type missing 'name' field")

        subtask = data.get("subtask", False)

        return IssueType(name=name, subtask=subtask)

    def _parse_status(self, data: Optional[Dict[str, Any]]) -> Status:
        """Parse status from JSON."""
        if not data:
            raise JiraParseError("Missing required field: status")

        name = data.get("name")
        if not name:
            raise JiraParseError("Status missing 'name' field")

        return Status(name=name)

    def _parse_project(self, data: Optional[Dict[str, Any]]) -> Project:
        """Parse project from JSON."""
        if not data:
            raise JiraParseError("Missing required field: project")

        key = data.get("key")
        if not key:
            raise JiraParseError("Project missing 'key' field")

        name = data.get("name")

        return Project(key=key, name=name)

    def _parse_user(self, data: Optional[Dict[str, Any]], field_name: str) -> User:
        """Parse user from JSON."""
        if not data:
            raise JiraParseError(f"Missing required field: {field_name}")

        display_name = data.get("displayName")
        if not display_name:
            raise JiraParseError(f"User ({field_name}) missing 'displayName' field")

        email_address = data.get("emailAddress")

        return User(display_name=display_name, email_address=email_address)

    def _parse_priority(self, data: Optional[Dict[str, Any]]) -> Optional[Priority]:
        """Parse priority from JSON."""
        if not data:
            return None

        name = data.get("name")
        if not name:
            return None

        return Priority(name=name)

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        if not value:
            return None

        try:
            # Jira uses ISO 8601 format: 2025-11-26T10:00:00.000+0000
            # Handle both with and without microseconds
            if "." in value:
                # With microseconds
                dt_str = value.split("+")[0].split("-", 3)[-1] if "+" in value else value.split("Z")[0]
                return datetime.fromisoformat(value.replace("+0000", "+00:00").replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(value.replace("+0000", "+00:00").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            # If parsing fails, return None rather than raising error
            return None

    def _parse_components(self, data: List[Dict[str, Any]]) -> List[Component]:
        """Parse components from JSON."""
        components = []
        for item in data:
            name = item.get("name")
            if name:
                components.append(Component(name=name))
        return components

    def _parse_comments(self, data: Dict[str, Any]) -> List[Comment]:
        """Parse comments from JSON."""
        comments = []
        comment_list = data.get("comments", [])

        for item in comment_list:
            try:
                author_data = item.get("author")
                if not author_data:
                    continue

                author = User(
                    display_name=author_data.get("displayName", "Unknown"),
                    email_address=author_data.get("emailAddress"),
                )

                body = item.get("body", "")
                created = self._parse_datetime(item.get("created"))

                if created:
                    comments.append(Comment(author=author, body=body, created=created))
            except Exception:
                # Skip malformed comments
                continue

        return comments

    def _parse_attachments(self, data: List[Dict[str, Any]]) -> List[Attachment]:
        """Parse attachments from JSON."""
        attachments = []
        for item in data:
            try:
                filename = item.get("filename")
                if not filename:
                    continue

                mime_type = item.get("mimeType")
                size = item.get("size")
                created = self._parse_datetime(item.get("created"))

                attachments.append(
                    Attachment(
                        filename=filename,
                        mime_type=mime_type,
                        size=size,
                        created=created,
                    )
                )
            except Exception:
                # Skip malformed attachments
                continue

        return attachments

    def _parse_subtasks(self, data: List[Dict[str, Any]]) -> List[Subtask]:
        """Parse subtasks from JSON."""
        subtasks = []
        for item in data:
            try:
                key = item.get("key")
                if not key:
                    continue

                # Subtask summary might be nested in fields
                summary = None
                if "fields" in item and isinstance(item["fields"], dict):
                    summary = item["fields"].get("summary")

                subtasks.append(Subtask(key=key, summary=summary))
            except Exception:
                # Skip malformed subtasks
                continue

        return subtasks

    def _extract_custom_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Extract custom fields (customfield_*) from fields dict."""
        custom_fields = {}

        for key, value in fields.items():
            if key.startswith("customfield_"):
                custom_fields[key] = value

        return custom_fields
