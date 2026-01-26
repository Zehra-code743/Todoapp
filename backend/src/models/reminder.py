"""
Reminder model for the Advanced Todo application.
Manages task reminders and scheduling.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from enum import Enum
from .task import Task


class ReminderStatusEnum(str, Enum):
    """Status values for reminders."""
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


class Reminder(SQLModel, table=True):
    """Model representing a reminder for a task."""

    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    scheduled_for: datetime = Field(sa_column_kwargs={"nullable": False})
    status: ReminderStatusEnum = Field(default=ReminderStatusEnum.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Task = Relationship(back_populates="reminders")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "task_id": 1,
                "user_id": "user_abc123",
                "scheduled_for": "2026-01-15T09:00:00Z",
                "status": "pending",
                "created_at": "2025-12-26T10:30:00Z"
            }
        }


def create_reminder_for_task(
    task: Task,
    reminder_advance_minutes: int = 60,
    notification_channels: Optional[list] = None
) -> Reminder:
    """
    Create a reminder for a task based on its due date.

    Args:
        task: Task to create reminder for
        reminder_advance_minutes: Minutes before due date to send reminder (default 60)
        notification_channels: List of notification channels (email, push, in_app)

    Returns:
        Reminder instance
    """
    if not task.due_date:
        raise ValueError("Cannot create reminder for task without due date")

    # Calculate when to schedule the reminder (advance notice before due date)
    scheduled_for = task.due_date - datetime.timedelta(minutes=reminder_advance_minutes)

    # Default notification settings if not provided
    reminder_settings = {
        "enabled": True,
        "advance_notice": reminder_advance_minutes,
        "notification_channels": notification_channels or ["push", "email"]
    }

    # Create the reminder
    reminder = Reminder(
        task_id=task.id,
        user_id=task.user_id,
        scheduled_for=scheduled_for,
        status=ReminderStatusEnum.PENDING
    )

    # Update task with reminder settings
    task.reminder_settings = reminder_settings
    task.reminder_sent = False

    return reminder


def is_reminder_overdue(reminder: Reminder) -> bool:
    """
    Check if a reminder is overdue (should have been sent).

    Args:
        reminder: Reminder to check

    Returns:
        True if reminder is overdue, False otherwise
    """
    if reminder.status != ReminderStatusEnum.PENDING:
        return False

    return datetime.utcnow() > reminder.scheduled_for


def is_reminder_upcoming(reminder: Reminder, within_minutes: int = 5) -> bool:
    """
    Check if a reminder is upcoming within a certain time window.

    Args:
        reminder: Reminder to check
        within_minutes: Time window in minutes (default 5)

    Returns:
        True if reminder is upcoming, False otherwise
    """
    if reminder.status != ReminderStatusEnum.PENDING:
        return False

    time_until_scheduled = reminder.scheduled_for - datetime.utcnow()
    return 0 <= time_until_scheduled.total_seconds() <= (within_minutes * 60)


def mark_reminder_as_sent(reminder: Reminder) -> None:
    """
    Mark a reminder as sent.

    Args:
        reminder: Reminder to update
    """
    reminder.status = ReminderStatusEnum.SENT


def cancel_reminder(reminder: Reminder) -> None:
    """
    Cancel a reminder.

    Args:
        reminder: Reminder to cancel
    """
    if reminder.status == ReminderStatusEnum.PENDING:
        reminder.status = ReminderStatusEnum.CANCELLED


def reschedule_reminder(reminder: Reminder, new_schedule_time: datetime) -> None:
    """
    Reschedule a pending reminder to a new time (e.g., for snooze functionality).

    Args:
        reminder: Reminder to reschedule
        new_schedule_time: New time for the reminder
    """
    if reminder.status == ReminderStatusEnum.PENDING:
        reminder.scheduled_for = new_schedule_time
    else:
        raise ValueError(f"Cannot reschedule reminder with status: {reminder.status}")


def should_send_reminder(reminder: Reminder) -> bool:
    """
    Determine if a reminder should be sent now.

    Args:
        reminder: Reminder to check

    Returns:
        True if reminder should be sent, False otherwise
    """
    return (
        reminder.status == ReminderStatusEnum.PENDING and
        datetime.utcnow() >= reminder.scheduled_for
    )


def get_reminder_notification_message(reminder: Reminder, task: Task) -> str:
    """
    Generate a notification message for a reminder.

    Args:
        reminder: Reminder to generate message for
        task: Associated task

    Returns:
        Notification message string
    """
    if task.due_date:
        return f"Reminder: '{task.title}' is due soon at {task.due_date.strftime('%Y-%m-%d %H:%M')}"
    else:
        return f"Reminder: Please complete '{task.title}'"