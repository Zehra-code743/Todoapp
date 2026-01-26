"""
Shared Data Models for the Advanced Todo Application
Defines the core entities used across all services
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, validator
import json


class PriorityEnum(str, Enum):
    """Enumeration of priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatusEnum(str, Enum):
    """Enumeration of task statuses"""
    PENDING = "pending"
    COMPLETED = "completed"


class NotificationChannelEnum(str, Enum):
    """Enumeration of notification channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class RecurrencePatternEnum(str, Enum):
    """Enumeration of recurrence patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RecurrenceSettings(BaseModel):
    """Configuration for recurring tasks"""
    pattern: RecurrencePatternEnum
    interval: int
    days: Optional[List[str]] = []  # Days of week for weekly recurrence (Mon, Tue, etc.)
    end_date: Optional[str] = None  # Format: YYYY-MM-DD

    @validator('interval')
    def validate_interval(cls, v):
        if v <= 0:
            raise ValueError('Interval must be greater than 0')
        return v


class ReminderSettings(BaseModel):
    """Configuration for task reminders"""
    offset_minutes: int
    channel: NotificationChannelEnum

    @validator('offset_minutes')
    def validate_offset_minutes(cls, v):
        if v < 0:
            raise ValueError('Offset minutes must be non-negative')
        return v


class TaskBase(BaseModel):
    """Base model for tasks without ID"""
    title: str
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.MEDIUM
    tags: Optional[List[str]] = []
    due_date: Optional[str] = None  # ISO 8601 format
    is_recurring: bool = False
    recurrence_settings: Optional[RecurrenceSettings] = None
    reminder_settings: Optional[ReminderSettings] = None

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 255:
            raise ValueError('Title must be 255 characters or less')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Tasks cannot have more than 10 tags')
        return v or []


class Task(TaskBase):
    """Full task model with ID and timestamps"""
    id: int
    user_id: str
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None

    @validator('due_date')
    def validate_due_date(cls, v):
        if v:
            try:
                # Try to parse the date to ensure it's valid
                from datetime import datetime
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Due date must be in ISO 8601 format')
        return v


class TaskUpdate(BaseModel):
    """Model for updating tasks"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None
    reminder_settings: Optional[ReminderSettings] = None

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Title cannot be empty')
            if len(v) > 255:
                raise ValueError('Title must be 255 characters or less')
        return v


class User(BaseModel):
    """User model"""
    id: str
    email: str
    name: Optional[str] = None
    created_at: str
    updated_at: str


class Event(BaseModel):
    """Event model for audit trail"""
    id: str
    event_type: str
    event_id: str
    timestamp: str
    user_id: str
    task_id: Optional[int] = None
    payload: dict

    @validator('event_type')
    def validate_event_type(cls, v):
        if not v:
            raise ValueError('Event type cannot be empty')
        return v


class Notification(BaseModel):
    """Notification model"""
    id: int
    task_id: int
    user_id: str
    title: str
    message: str
    channel: NotificationChannelEnum
    scheduled_at: str
    sent_at: Optional[str] = None
    status: str = "pending"  # pending, sent, failed
    created_at: str
    updated_at: str

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ["pending", "sent", "failed"]
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v


class ApiResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


class ApiError(BaseModel):
    """Standard API error model"""
    error: str
    details: Optional[dict] = None
    code: Optional[str] = None


class TaskSearchRequest(BaseModel):
    """Request model for task search"""
    query: str
    limit: int = 20
    offset: int = 0


class TaskFilterRequest(BaseModel):
    """Request model for task filtering"""
    status: Optional[TaskStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    tag: Optional[str] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    due_after: Optional[str] = None
    due_before: Optional[str] = None


class TaskSortRequest(BaseModel):
    """Request model for task sorting"""
    field: str = "created_at"  # created_at, due_date, priority, title
    order: str = "desc"  # asc, desc


# Example usage and validation
if __name__ == "__main__":
    # Example of creating a task
    task_data = {
        "title": "Sample Task",
        "description": "This is a sample task",
        "priority": "high",
        "tags": ["work", "important"],
        "due_date": "2024-12-31T10:00:00Z",
        "is_recurring": True,
        "recurrence_settings": {
            "pattern": "weekly",
            "interval": 1,
            "days": ["Mon", "Wed", "Fri"],
            "end_date": "2025-12-31"
        },
        "reminder_settings": {
            "offset_minutes": 30,
            "channel": "email"
        },
        "user_id": "user123",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }

    task = Task(**task_data)
    print(f"Created task: {task.title} with priority {task.priority}")
    print(f"Tags: {task.tags}")
    print(f"Recurring: {task.is_recurring}")
    print(f"Recurrence settings: {task.recurrence_settings}")
    print(f"Reminder settings: {task.reminder_settings}")