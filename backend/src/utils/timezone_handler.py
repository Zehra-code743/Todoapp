"""
Timezone handling utilities for the Advanced Todo application.
Manages timezone conversions and storage according to specification.
"""
from datetime import datetime, timezone, timedelta
from typing import Union, Optional
import pytz
import os


class TimezoneHandler:
    """
    Handles timezone conversions and storage for the application.
    Implements the requirement to store all timestamps in UTC
    and display them in the user's local timezone.
    """

    @staticmethod
    def convert_to_utc(dt: Union[datetime, str], user_timezone: Optional[str] = None) -> datetime:
        """
        Convert a datetime from user's timezone to UTC.

        Args:
            dt: Datetime object or ISO string to convert
            user_timezone: User's timezone (e.g., 'America/New_York').
                          Defaults to UTC if not provided.

        Returns:
            DateTime in UTC timezone
        """
        if isinstance(dt, str):
            # Parse ISO format string
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

        if dt.tzinfo is None:
            # Assume naive datetime is in user's timezone
            if user_timezone:
                tz = pytz.timezone(user_timezone)
                dt = tz.localize(dt)
            else:
                # Default to UTC for naive datetimes
                dt = dt.replace(tzinfo=timezone.utc)

        # Convert to UTC if not already
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt

    @staticmethod
    def convert_from_utc_to_user_tz(utc_dt: datetime, user_timezone: str = 'UTC') -> datetime:
        """
        Convert a UTC datetime to user's local timezone.

        Args:
            utc_dt: Datetime in UTC
            user_timezone: User's timezone (e.g., 'America/New_York')

        Returns:
            DateTime in user's timezone
        """
        if utc_dt.tzinfo is None:
            # If datetime is naive, assume it's already in UTC
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)

        user_tz = pytz.timezone(user_timezone)
        user_dt = utc_dt.astimezone(user_tz)
        return user_dt

    @staticmethod
    def get_current_time_in_timezone(user_timezone: str = 'UTC') -> datetime:
        """
        Get current time in the specified timezone.

        Args:
            user_timezone: Timezone to get current time in

        Returns:
            Current datetime in specified timezone
        """
        utc_now = datetime.now(timezone.utc)
        user_tz = pytz.timezone(user_timezone)
        return utc_now.astimezone(user_tz)

    @staticmethod
    def validate_timezone(timezone_str: str) -> bool:
        """
        Validate if the provided timezone string is valid.

        Args:
            timezone_str: Timezone string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False

    @staticmethod
    def get_timezone_offset(user_timezone: str = 'UTC') -> float:
        """
        Get the UTC offset for the specified timezone in hours.

        Args:
            user_timezone: Timezone to get offset for

        Returns:
            UTC offset in hours
        """
        user_tz = pytz.timezone(user_timezone)
        now = datetime.now(user_tz)
        offset_seconds = now.utcoffset().total_seconds()
        return offset_seconds / 3600

    @staticmethod
    def format_datetime_for_display(dt: Union[datetime, str],
                                  user_timezone: str = 'UTC',
                                  format_string: str = '%Y-%m-%d %H:%M:%S %Z') -> str:
        """
        Format a datetime for display in the user's timezone.

        Args:
            dt: Datetime object or ISO string to format
            user_timezone: User's timezone
            format_string: Format string for output

        Returns:
            Formatted datetime string
        """
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

        if dt.tzinfo is None:
            # Assume naive datetime is in UTC
            dt = dt.replace(tzinfo=timezone.utc)

        user_dt = TimezoneHandler.convert_from_utc_to_user_tz(dt, user_timezone)
        return user_dt.strftime(format_string)

    @staticmethod
    def get_business_hours_start(user_timezone: str = 'UTC',
                               start_hour: int = 9) -> datetime:
        """
        Get the start of business hours for today in user's timezone.

        Args:
            user_timezone: User's timezone
            start_hour: Hour when business starts (default 9 AM)

        Returns:
            Datetime for start of business hours today
        """
        user_tz = pytz.timezone(user_timezone)
        now = datetime.now(user_tz)

        business_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        return business_start

    @staticmethod
    def get_business_hours_end(user_timezone: str = 'UTC',
                             end_hour: int = 17) -> datetime:
        """
        Get the end of business hours for today in user's timezone.

        Args:
            user_timezone: User's timezone
            end_hour: Hour when business ends (default 5 PM)

        Returns:
            Datetime for end of business hours today
        """
        user_tz = pytz.timezone(user_timezone)
        now = datetime.now(user_tz)

        business_end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        return business_end

    @staticmethod
    def is_dst_transition(date_time: datetime, user_timezone: str = 'UTC') -> bool:
        """
        Check if the given datetime is during a DST transition.

        Args:
            date_time: Datetime to check
            user_timezone: User's timezone

        Returns:
            True if during DST transition, False otherwise
        """
        user_tz = pytz.timezone(user_timezone)
        localized_dt = user_tz.localize(date_time, is_dst=None)

        # Check if the timezone is currently observing DST
        return bool(localized_dt.dst())


# Convenience functions for common operations
def utc_now() -> datetime:
    """Get current time in UTC."""
    return datetime.now(timezone.utc)


def user_time_now(user_timezone: str = 'UTC') -> datetime:
    """Get current time in user's timezone."""
    return TimezoneHandler.get_current_time_in_timezone(user_timezone)


def convert_to_utc_wrapper(dt: Union[datetime, str], user_timezone: Optional[str] = None) -> datetime:
    """Wrapper for converting datetime to UTC."""
    return TimezoneHandler.convert_to_utc(dt, user_timezone)


def convert_from_utc_to_user_tz_wrapper(utc_dt: datetime, user_timezone: str = 'UTC') -> datetime:
    """Wrapper for converting UTC datetime to user's timezone."""
    return TimezoneHandler.convert_from_utc_to_user_tz(utc_dt, user_timezone)