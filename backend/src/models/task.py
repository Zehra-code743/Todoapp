"""
Task model for the Advanced Todo application.
Represents the core task entity with all its attributes and relationships.
Extends the basic task model with advanced features: recurring tasks, due dates, reminders, priorities, and tags.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PriorityEnum(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(SQLModel, table=True):
    """Task entity with advanced features: recurring tasks, due dates, reminders, priorities, and tags."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=500)  # Increased max length per spec
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)

    # Priority field (new)
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)

    # Tags field (new) - using a separate table for tags with many-to-many relationship
    # Note: We'll handle tags separately as a many-to-many relationship
    # Relationship to tags through association table

    # Category field (new)
    category: Optional[str] = Field(default=None, max_length=100)

    # Due date and reminder functionality (new)
    due_date: Optional[datetime] = Field(default=None)
    reminder_sent: bool = Field(default=False)

    # Recurring task functionality (new)
    is_recurring: bool = Field(default=False)
    # We'll store recurrence pattern as JSON in a separate field
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")  # For recurring tasks
    next_occurrence_date: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    # Relationship to reminders
    reminders: List["Reminder"] = Relationship(back_populates="task")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_abc123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "medium",
                "category": "personal",
                "due_date": "2026-01-15T10:00:00Z",
                "reminder_sent": False,
                "is_recurring": False,
                "parent_task_id": None,
                "next_occurrence_date": None,
                "created_at": "2025-12-26T10:30:00Z",
                "updated_at": "2025-12-26T10:30:00Z",
                "completed_at": None
            }
        }
