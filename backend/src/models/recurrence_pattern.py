"""
RecurrencePattern model for the Advanced Todo application.
Defines the structure for recurrence patterns used in recurring tasks.
"""
from sqlmodel import SQLModel, Field
from typing import Optional, List
from enum import Enum


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
    """
    Model representing a recurrence pattern.
    This is a data structure rather than a database table since it's stored as JSON in the Task model.
    """

    type: RecurrenceTypeEnum
    interval: int  # e.g., every 2 weeks
    days_of_week: Optional[List[int]] = None  # [0-6] for Sunday-Saturday
    day_of_month: Optional[int] = None  # 1-31
    end_condition: Optional[dict] = None  # {type: EndConditionTypeEnum, value: int/datetime}


def validate_recurrence_pattern(pattern: RecurrencePattern) -> List[str]:
    """
    Validate a recurrence pattern according to the data model specification.

    Args:
        pattern: Recurrence pattern to validate

    Returns:
        List of validation errors
    """
    errors = []

    # Validate type
    if not pattern.type:
        errors.append("Recurrence pattern type is required")
    elif pattern.type not in RecurrenceTypeEnum:
        errors.append(f"Invalid recurrence type '{pattern.type}'. Must be one of {list(RecurrenceTypeEnum)}")

    # Validate interval
    if pattern.interval is None or pattern.interval <= 0:
        errors.append("Interval must be a positive integer")

    # Validate type-specific fields
    if pattern.type == RecurrenceTypeEnum.WEEKLY:
        if pattern.days_of_week is not None:
            if not isinstance(pattern.days_of_week, list):
                errors.append("days_of_week must be a list")
            else:
                for day in pattern.days_of_week:
                    if not isinstance(day, int) or day < 0 or day > 6:
                        errors.append("days_of_week must contain integers between 0-6 (Sunday=0)")

    elif pattern.type == RecurrenceTypeEnum.MONTHLY:
        if pattern.day_of_month is not None:
            if not isinstance(pattern.day_of_month, int) or pattern.day_of_month < 1 or pattern.day_of_month > 31:
                errors.append("day_of_month must be an integer between 1-31")

    # Validate end condition if present
    if pattern.end_condition:
        if not isinstance(pattern.end_condition, dict):
            errors.append("end_condition must be a dictionary")
        else:
            end_type = pattern.end_condition.get("type")
            valid_end_types = list(EndConditionTypeEnum)

            if end_type not in valid_end_types:
                errors.append(f"Invalid end condition type '{end_type}'. Must be one of {valid_end_types}")

            if end_type == EndConditionTypeEnum.AFTER_N_OCCURRENCES.value:
                value = pattern.end_condition.get("value")
                if not isinstance(value, int) or value <= 0:
                    errors.append("end_condition.value must be a positive integer for 'after_n_occurrences'")

    return errors


def create_daily_pattern(interval: int = 1) -> RecurrencePattern:
    """
    Create a daily recurrence pattern.

    Args:
        interval: Interval in days (default 1 for every day)

    Returns:
        Daily recurrence pattern
    """
    return RecurrencePattern(
        type=RecurrenceTypeEnum.DAILY,
        interval=interval
    )


def create_weekly_pattern(interval: int = 1, days_of_week: List[int] = None) -> RecurrencePattern:
    """
    Create a weekly recurrence pattern.

    Args:
        interval: Interval in weeks (default 1 for every week)
        days_of_week: List of days [0-6] where 0 is Sunday (default [0] for Sundays)

    Returns:
        Weekly recurrence pattern
    """
    if days_of_week is None:
        days_of_week = [0]  # Default to Sunday

    return RecurrencePattern(
        type=RecurrenceTypeEnum.WEEKLY,
        interval=interval,
        days_of_week=days_of_week
    )


def create_monthly_pattern(interval: int = 1, day_of_month: int = None) -> RecurrencePattern:
    """
    Create a monthly recurrence pattern.

    Args:
        interval: Interval in months (default 1 for every month)
        day_of_month: Day of month (1-31, default None)

    Returns:
        Monthly recurrence pattern
    """
    return RecurrencePattern(
        type=RecurrenceTypeEnum.MONTHLY,
        interval=interval,
        day_of_month=day_of_month
    )


def create_custom_pattern(interval: int) -> RecurrencePattern:
    """
    Create a custom recurrence pattern.

    Args:
        interval: Interval in days for custom pattern

    Returns:
        Custom recurrence pattern
    """
    return RecurrencePattern(
        type=RecurrenceTypeEnum.CUSTOM,
        interval=interval
    )


def has_end_condition(pattern: RecurrencePattern) -> bool:
    """
    Check if a recurrence pattern has an end condition.

    Args:
        pattern: Recurrence pattern to check

    Returns:
        True if pattern has an end condition, False otherwise
    """
    return pattern.end_condition is not None


def is_infinite_pattern(pattern: RecurrencePattern) -> bool:
    """
    Check if a recurrence pattern is infinite (never ends).

    Args:
        pattern: Recurrence pattern to check

    Returns:
        True if pattern is infinite, False otherwise
    """
    if not has_end_condition(pattern):
        return True

    return (
        pattern.end_condition.get("type") == EndConditionTypeEnum.NEVER.value or
        pattern.end_condition.get("type") == EndConditionTypeEnum.never
    )