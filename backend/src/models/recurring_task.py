"""
RecurringTask model for the Advanced Todo application.
Extends Task functionality with recurrence patterns and scheduling.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from .task import Task


class RecurrenceTypeEnum(str, Enum):
    """Types of recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class EndConditionTypeEnum(str, Enum):
    """Types of end conditions for recurring tasks."""
    NEVER = "never"
    AFTER_N_OCCURRENCES = "after_n_occurrences"
    BY_DATE = "by_date"


class RecurrencePattern(SQLModel):
    """Model representing a recurrence pattern."""
    type: RecurrenceTypeEnum
    interval: int  # e.g., every 2 weeks
    days_of_week: Optional[List[int]] = None  # [0-6] for Sunday-Saturday
    day_of_month: Optional[int] = None  # 1-31
    end_condition: Optional[Dict[str, Any]] = None  # {type: EndConditionTypeEnum, value: int/datetime}


# In practice, we'll use the Task model directly with is_recurring=True
# This class is kept for reference but not used as a table
class RecurringTask:
    """
    RecurringTask model that represents recurring task concepts.
    In practice, we use the Task model with is_recurring=True,
    but this class provides methods and logic specific to recurring tasks.
    """

    @staticmethod
    def from_task(task: Task) -> 'RecurringTask':
        """
        Convert a Task instance to a RecurringTask representation.

        Args:
            task: Task instance to convert

        Returns:
            RecurringTask representation
        """
        if not task.is_recurring:
            raise ValueError("Task is not a recurring task")
        recurring_task = RecurringTask()
        recurring_task.__dict__.update(task.__dict__)
        return recurring_task


# For practical implementation, we'll often work with the Task model directly
# and use the is_recurring field to determine if it's a recurring task
def is_recurring_task(task: Task) -> bool:
    """
    Check if a task is a recurring task.

    Args:
        task: Task instance to check

    Returns:
        True if the task is recurring, False otherwise
    """
    return task.is_recurring and task.recurrence_pattern is not None


def get_next_occurrence_date(task: Task) -> Optional[datetime]:
    """
    Calculate the next occurrence date for a recurring task.

    Args:
        task: Recurring task to calculate next occurrence for

    Returns:
        Next occurrence date or None if not recurring
    """
    if not is_recurring_task(task) or not task.recurrence_pattern:
        return None

    # This would normally call the recurrence calculator
    # For now, we'll return a placeholder implementation
    from ..utils.recurrence_calculator import calculate_next_occurrence

    # Use the last occurrence date (either created_at or completed_at) as the basis
    last_occurrence = task.completed_at or task.created_at

    return calculate_next_occurrence(last_occurrence, task.recurrence_pattern)


def create_next_occurrence(task: Task) -> Optional[Task]:
    """
    Create the next occurrence of a recurring task.

    Args:
        task: Completed recurring task to create next occurrence for

    Returns:
        New task instance for the next occurrence, or None if no more occurrences
    """
    if not is_recurring_task(task):
        return None

    next_date = get_next_occurrence_date(task)
    if next_date is None:
        return None

    # Create a new task with the same properties but for the next occurrence
    new_task = Task(
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        due_date=next_date if task.due_date else None,  # Adjust due date to match new occurrence
        is_recurring=task.is_recurring,
        recurrence_pattern=task.recurrence_pattern,
        parent_task_id=task.id if task.parent_task_id is None else task.parent_task_id,
        next_occurrence_date=get_next_occurrence_date(task)  # Calculate the next after this one
    )

    return new_task