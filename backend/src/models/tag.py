"""
Tag model for the Advanced Todo application.
Manages task categorization through tags.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Tag(SQLModel, table=True):
    """Model representing a tag that can be associated with tasks."""

    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100, unique=True)
    user_id: Optional[str] = Field(default=None, foreign_key="users.id")  # For personal tags
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "work",
                "user_id": "user_abc123",
                "created_at": "2025-12-26T10:30:00Z"
            }
        }


def validate_tag_name(name: str) -> bool:
    """
    Validate a tag name.

    Args:
        name: Tag name to validate

    Returns:
        True if valid, False otherwise
    """
    if not name or len(name.strip()) == 0:
        return False

    if len(name) > 100:
        return False

    # Additional validation could be added here
    return True


def normalize_tag_name(name: str) -> str:
    """
    Normalize a tag name (e.g., lowercase, trim whitespace).

    Args:
        name: Raw tag name

    Returns:
        Normalized tag name
    """
    return name.strip().lower()


def is_personal_tag(tag: Tag) -> bool:
    """
    Check if a tag is personal (associated with a specific user).

    Args:
        tag: Tag to check

    Returns:
        True if personal tag, False if global
    """
    return tag.user_id is not None