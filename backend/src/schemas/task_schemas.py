"""
Pydantic schemas for Task CRUD operations
Request and response models for API endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PriorityEnum(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCreate(BaseModel):
    """Request body for creating a new task"""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Optional task description"
    )
    priority: Optional[PriorityEnum] = Field(default="medium", description="Task priority")
    tags: Optional[List[str]] = Field(default=[], description="Task tags")
    category: Optional[str] = Field(default=None, max_length=100, description="Task category")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "medium",
                "tags": ["shopping", "food"],
                "category": "personal",
                "due_date": "2026-01-15T10:00:00Z"
            }
        }


class RecurringTaskCreate(TaskCreate):
    """Request body for creating a new recurring task"""

    recurrence_pattern: dict = Field(..., description="Recurrence pattern for the task")
    first_occurrence_date: Optional[datetime] = Field(default=None, description="Date for the first occurrence")


class TaskUpdate(BaseModel):
    """Request body for updating a task"""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[PriorityEnum] = Field(default=None, description="Task priority")
    tags: Optional[List[str]] = Field(default=None, description="Task tags")
    category: Optional[str] = Field(default=None, max_length=100, description="Task category")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and fruits",
                "description": "Updated list",
                "priority": "high",
                "tags": ["shopping", "food", "urgent"],
                "category": "personal",
                "due_date": "2026-01-15T10:00:00Z"
            }
        }


class SetDueDateRequest(BaseModel):
    """Request body for setting due date with reminder"""

    task_id: int = Field(..., description="ID of the task to set due date for")
    due_date: str = Field(..., description="Due date in ISO format")
    reminder_enabled: bool = Field(default=True, description="Whether to schedule a reminder")
    reminder_advance_minutes: int = Field(default=60, description="Minutes before due date to send reminder")


class TaskResponse(BaseModel):
    """Response model for a single task"""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: Optional[PriorityEnum] = "medium"
    tags: Optional[List[str]] = []
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    reminder_sent: bool = False
    is_recurring: bool = False
    recurrence_pattern: Optional[dict] = None
    parent_task_id: Optional[int] = None
    next_occurrence_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_abc123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "medium",
                "tags": ["shopping", "food"],
                "category": "personal",
                "due_date": "2026-01-15T10:00:00Z",
                "reminder_sent": False,
                "is_recurring": False,
                "recurrence_pattern": None,
                "parent_task_id": None,
                "next_occurrence_date": None,
                "created_at": "2025-12-26T10:30:00Z",
                "updated_at": "2025-12-26T10:30:00Z",
                "completed_at": None
            }
        }


class TaskListResponse(BaseModel):
    """Response model for listing tasks"""

    tasks: List[TaskResponse]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "user_id": "user_abc123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "priority": "medium",
                        "tags": ["shopping", "food"],
                        "category": "personal",
                        "due_date": "2026-01-15T10:00:00Z",
                        "reminder_sent": False,
                        "is_recurring": False,
                        "recurrence_pattern": None,
                        "parent_task_id": None,
                        "next_occurrence_date": None,
                        "created_at": "2025-12-26T10:30:00Z",
                        "updated_at": "2025-12-26T10:30:00Z",
                        "completed_at": None
                    }
                ],
                "count": 1,
            }
        }
