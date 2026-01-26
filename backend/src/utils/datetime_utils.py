"""
DateTime utility functions for the Advanced Todo application.
Provides common datetime operations and helpers.
"""
from datetime import datetime, timedelta
from typing import Optional, Union
import calendar


def parse_iso_datetime(iso_string: str) -> datetime:
    """
    Parse an ISO format datetime string to datetime object.
    Handles various ISO formats including those with 'Z' suffix.

    Args:
        iso_string: ISO format datetime string

    Returns:
        Parsed datetime object
    """
    # Replace 'Z' with '+00:00' for proper parsing
    if iso_string.endswith('Z'):
        iso_string = iso_string[:-1] + '+00:00'

    # Handle microseconds if present
    if '.' in iso_string and '+' in iso_string:
        # Format: YYYY-MM-DDTHH:MM:SS.ffffff+HH:MM
        return datetime.fromisoformat(iso_string)
    elif '+' in iso_string:
        # Format: YYYY-MM-DDTHH:MM:SS+HH:MM
        return datetime.fromisoformat(iso_string)
    elif 'T' in iso_string and len(iso_string) == 19:
        # Format: YYYY-MM-DDTHH:MM:SS (naive)
        return datetime.fromisoformat(iso_string)
    else:
        # Try parsing as date only and set time to 00:00:00
        try:
            date_part = datetime.fromisoformat(iso_string)
            return date_part
        except ValueError:
            raise ValueError(f"Unable to parse datetime string: {iso_string}")


def get_next_occurrence(
    current_date: datetime,
    recurrence_type: str,
    interval: int = 1,
    days_of_week: Optional[list] = None,
    day_of_month: Optional[int] = None
) -> datetime:
    """
    Calculate the next occurrence date based on recurrence pattern.

    Args:
        current_date: Current occurrence date
        recurrence_type: Type of recurrence ('daily', 'weekly', 'monthly', 'custom')
        interval: Interval multiplier (e.g., every 2 weeks)
        days_of_week: Days of week for weekly recurrence [0-6, where 0 is Sunday]
        day_of_month: Day of month for monthly recurrence [1-31]

    Returns:
        Next occurrence date
    """
    if recurrence_type == 'daily':
        return current_date + timedelta(days=interval)

    elif recurrence_type == 'weekly':
        # For weekly recurrence, we need to find the next occurrence of the same day of week
        if days_of_week:
            # Find the next occurrence of any of the specified days
            next_date = current_date + timedelta(days=1)

            # Keep incrementing days until we find a matching day of week
            while next_date.weekday() not in days_of_week:
                next_date += timedelta(days=1)
            return next_date
        else:
            # Default to same day of week after interval weeks
            return current_date + timedelta(weeks=interval)

    elif recurrence_type == 'monthly':
        if day_of_month:
            # Find the next month with the specified day
            next_month = current_date.month + interval
            next_year = current_date.year

            # Adjust year if needed
            while next_month > 12:
                next_month -= 12
                next_year += 1

            # Handle day overflow (e.g., Jan 31 -> Feb 31 doesn't exist)
            max_day = calendar.monthrange(next_year, next_month)[1]
            actual_day = min(day_of_month, max_day)

            return current_date.replace(year=next_year, month=next_month, day=actual_day)
        else:
            # Default to same day of month after interval months
            next_date = current_date
            for _ in range(interval):
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
            return next_date

    elif recurrence_type == 'custom':
        # For custom recurrence, interpret interval as days
        return current_date + timedelta(days=interval)

    else:
        raise ValueError(f"Unsupported recurrence type: {recurrence_type}")


def is_date_in_past(date: datetime, reference_date: Optional[datetime] = None) -> bool:
    """
    Check if a date is in the past compared to a reference date.

    Args:
        date: Date to check
        reference_date: Reference date (defaults to now())

    Returns:
        True if date is in the past, False otherwise
    """
    if reference_date is None:
        reference_date = datetime.now()

    return date < reference_date


def is_date_in_future(date: datetime, reference_date: Optional[datetime] = None) -> bool:
    """
    Check if a date is in the future compared to a reference date.

    Args:
        date: Date to check
        reference_date: Reference date (defaults to now())

    Returns:
        True if date is in the future, False otherwise
    """
    if reference_date is None:
        reference_date = datetime.now()

    return date > reference_date


def get_time_until(date: datetime, reference_date: Optional[datetime] = None) -> timedelta:
    """
    Get the time difference between two dates.

    Args:
        date: Target date
        reference_date: Reference date (defaults to now())

    Returns:
        Time difference as timedelta
    """
    if reference_date is None:
        reference_date = datetime.now()

    return date - reference_date


def format_duration(td: timedelta) -> str:
    """
    Format a timedelta into a human-readable string.

    Args:
        td: Timedelta to format

    Returns:
        Human-readable duration string
    """
    total_seconds = int(td.total_seconds())

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    if not parts:
        return "0 seconds"

    return ", ".join(parts)


def add_business_days(start_date: datetime, business_days: int) -> datetime:
    """
    Add business days to a date, excluding weekends.

    Args:
        start_date: Starting date
        business_days: Number of business days to add

    Returns:
        New date after adding business days
    """
    current_date = start_date
    added_days = 0

    while added_days < business_days:
        current_date += timedelta(days=1)
        # Monday is 0, Sunday is 6
        if current_date.weekday() < 5:  # Monday to Friday
            added_days += 1

    return current_date


def get_start_of_day(dt: datetime) -> datetime:
    """
    Get the start of the day (00:00:00) for a given datetime.

    Args:
        dt: Input datetime

    Returns:
        Datetime with time set to 00:00:00
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: datetime) -> datetime:
    """
    Get the end of the day (23:59:59) for a given datetime.

    Args:
        dt: Input datetime

    Returns:
        Datetime with time set to 23:59:59
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_start_of_week(dt: datetime) -> datetime:
    """
    Get the start of the week (Monday 00:00:00) for a given datetime.

    Args:
        dt: Input datetime

    Returns:
        Datetime for the start of the week
    """
    start_of_day = get_start_of_day(dt)
    days_since_monday = start_of_day.weekday()
    return start_of_day - timedelta(days=days_since_monday)


def get_start_of_month(dt: datetime) -> datetime:
    """
    Get the start of the month (first day 00:00:00) for a given datetime.

    Args:
        dt: Input datetime

    Returns:
        Datetime for the start of the month
    """
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_start_of_year(dt: datetime) -> datetime:
    """
    Get the start of the year (January 1st 00:00:00) for a given datetime.

    Args:
        dt: Input datetime

    Returns:
        Datetime for the start of the year
    """
    return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def get_nearest_weekday(target_date: datetime, weekday: int) -> datetime:
    """
    Get the nearest occurrence of a specific weekday from a target date.
    Weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday

    Args:
        target_date: Reference date
        weekday: Target weekday (0-6)

    Returns:
        Nearest occurrence of the specified weekday
    """
    current_weekday = target_date.weekday()
    days_diff = (weekday - current_weekday) % 7

    if days_diff == 0:
        # If it's already the target weekday, return the same date
        return get_start_of_day(target_date)

    return get_start_of_day(target_date + timedelta(days=days_diff))


def is_weekend(dt: datetime) -> bool:
    """
    Check if a date falls on a weekend.

    Args:
        dt: Input datetime

    Returns:
        True if date is Saturday or Sunday, False otherwise
    """
    return dt.weekday() >= 5  # Saturday is 5, Sunday is 6


def is_weekday(dt: datetime) -> bool:
    """
    Check if a date falls on a weekday.

    Args:
        dt: Input datetime

    Returns:
        True if date is Monday to Friday, False otherwise
    """
    return dt.weekday() < 5  # Monday is 0, Friday is 4


def get_age(birth_date: datetime, reference_date: Optional[datetime] = None) -> int:
    """
    Calculate age in years between two dates.

    Args:
        birth_date: Birth date
        reference_date: Reference date (defaults to now())

    Returns:
        Age in years
    """
    if reference_date is None:
        reference_date = datetime.now()

    age = reference_date.year - birth_date.year
    # Subtract one year if birthday hasn't occurred this year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age