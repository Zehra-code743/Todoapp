"""Task entity module for todo console application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique identifier (auto-generated, immutable)
        title: Short description (1-200 characters, required)
        description: Detailed description (max 1000 characters, optional)
        completed: Completion status (default: False)
        created_at: Creation timestamp (auto-generated, immutable)
    """
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate task fields after initialization."""
        is_valid, error = validate_title(self.title)
        if not is_valid:
            raise ValueError(error)

        if self.description:
            is_valid, error = validate_description(self.description)
            if not is_valid:
                raise ValueError(error)


def validate_title(title: str) -> tuple[bool, str]:
    """
    Validate task title.

    Args:
        title: Title string to validate

    Returns:
        Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, error_message) if invalid
    """
    if not title or not title.strip():
        return False, "Title is required"
    if len(title) > 200:
        return False, "Title must be 1-200 characters"
    return True, ""


def validate_description(description: str) -> tuple[bool, str]:
    """
    Validate task description.

    Args:
        description: Description string to validate

    Returns:
        Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, error_message) if invalid
    """
    if len(description) > 1000:
        return False, "Description must be max 1000 characters"
    return True, ""
