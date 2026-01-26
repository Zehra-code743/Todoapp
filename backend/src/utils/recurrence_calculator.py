"""
Recurrence calculation utilities for the Advanced Todo application.
Handles the complex logic for calculating recurring task occurrences.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import calendar


class RecurrenceType(Enum):
    """Enumeration of supported recurrence types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class EndConditionType(Enum):
    """Enumeration of end condition types."""
    NEVER = "never"
    AFTER_N_OCCURRENCES = "after_n_occurrences"
    BY_DATE = "by_date"


class RecurrenceCalculator:
    """
    Calculates recurrence patterns for recurring tasks.
    Implements the logic defined in the data model for recurrence patterns.
    """

    @staticmethod
    def calculate_next_occurrence(
        current_date: datetime,
        recurrence_pattern: Dict[str, Any]
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence date based on the recurrence pattern.

        Args:
            current_date: Current occurrence date
            recurrence_pattern: Dictionary containing recurrence pattern details

        Returns:
            Next occurrence date or None if no more occurrences
        """
        recurrence_type = recurrence_pattern.get("type")
        interval = recurrence_pattern.get("interval", 1)
        days_of_week = recurrence_pattern.get("days_of_week")
        day_of_month = recurrence_pattern.get("day_of_month")

        # Check if there's an end condition
        end_condition = recurrence_pattern.get("end_condition")
        if end_condition:
            if RecurrenceCalculator.is_end_condition_met(end_condition, current_date):
                return None

        # Calculate next occurrence based on type
        if recurrence_type == "daily":
            next_date = current_date + timedelta(days=interval)
        elif recurrence_type == "weekly":
            if days_of_week:
                # Find the next occurrence of any of the specified days
                next_date = current_date + timedelta(days=1)

                # Keep incrementing days until we find a matching day of week
                while next_date.weekday() not in days_of_week:
                    next_date += timedelta(days=1)
            else:
                # Default to same day of week after interval weeks
                next_date = current_date + timedelta(weeks=interval)
        elif recurrence_type == "monthly":
            if day_of_month:
                # Calculate next month with the specific day
                next_month = current_date.month + interval
                next_year = current_date.year

                # Adjust year if needed
                while next_month > 12:
                    next_month -= 12
                    next_year += 1

                # Handle day overflow (e.g., Jan 31 -> Feb 31 doesn't exist)
                max_day = calendar.monthrange(next_year, next_month)[1]
                actual_day = min(day_of_month, max_day)

                next_date = current_date.replace(
                    year=next_year,
                    month=next_month,
                    day=actual_day
                )
            else:
                # Default to same day of month after interval months
                next_date = RecurrenceCalculator._add_months(current_date, interval)
        elif recurrence_type == "custom":
            # For custom, interpret interval as days
            next_date = current_date + timedelta(days=interval)
        else:
            raise ValueError(f"Unsupported recurrence type: {recurrence_type}")

        # Verify the calculated date doesn't exceed end conditions
        if end_condition and end_condition.get("type") == "by_date":
            end_date = end_condition.get("value")
            if isinstance(end_date, str):
                from .datetime_utils import parse_iso_datetime
                end_date = parse_iso_datetime(end_date)

            if next_date > end_date:
                return None

        return next_date

    @staticmethod
    def _add_months(source_date: datetime, months: int) -> datetime:
        """
        Helper method to add months to a date, handling month/year rollovers.

        Args:
            source_date: Starting date
            months: Number of months to add

        Returns:
            New date after adding months
        """
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1

        # Handle day overflow (e.g., Jan 31 + 1 month -> Feb 28/29)
        day = min(source_date.day, calendar.monthrange(year, month)[1])

        return source_date.replace(year=year, month=month, day=day)

    @staticmethod
    def calculate_all_occurrences(
        start_date: datetime,
        recurrence_pattern: Dict[str, Any],
        max_occurrences: int = 100
    ) -> List[datetime]:
        """
        Calculate all occurrences of a recurring task up to a limit.

        Args:
            start_date: First occurrence date
            recurrence_pattern: Dictionary containing recurrence pattern details
            max_occurrences: Maximum number of occurrences to calculate

        Returns:
            List of all occurrence dates
        """
        occurrences = [start_date]
        current_date = start_date

        for _ in range(max_occurrences - 1):
            next_date = RecurrenceCalculator.calculate_next_occurrence(
                current_date,
                recurrence_pattern
            )

            if next_date is None:
                break

            occurrences.append(next_date)
            current_date = next_date

        return occurrences

    @staticmethod
    def is_end_condition_met(end_condition: Dict[str, Any], current_date: datetime) -> bool:
        """
        Check if the end condition is met for a recurrence pattern.

        Args:
            end_condition: Dictionary containing end condition details
            current_date: Current date to check against

        Returns:
            True if end condition is met, False otherwise
        """
        end_type = end_condition.get("type")

        if end_type == "never":
            return False
        elif end_type == "after_n_occurrences":
            # This check would typically be done elsewhere since we need to track occurrence count
            # For now, return False to indicate no automatic end
            return False
        elif end_type == "by_date":
            end_date = end_condition.get("value")
            if isinstance(end_date, str):
                from .datetime_utils import parse_iso_datetime
                end_date = parse_iso_datetime(end_date)

            return current_date.date() >= end_date.date()
        else:
            return False

    @staticmethod
    def validate_recurrence_pattern(recurrence_pattern: Dict[str, Any]) -> List[str]:
        """
        Validate a recurrence pattern and return a list of validation errors.

        Args:
            recurrence_pattern: Dictionary containing recurrence pattern details

        Returns:
            List of validation error messages
        """
        errors = []

        # Check required fields
        if "type" not in recurrence_pattern:
            errors.append("Recurrence pattern must include 'type'")
            return errors  # Can't proceed without type

        recurrence_type = recurrence_pattern["type"]

        # Validate type
        valid_types = ["daily", "weekly", "monthly", "custom"]
        if recurrence_type not in valid_types:
            errors.append(f"Invalid recurrence type '{recurrence_type}'. Must be one of {valid_types}")

        # Validate interval
        interval = recurrence_pattern.get("interval", 1)
        if not isinstance(interval, (int, float)) or interval <= 0:
            errors.append("Interval must be a positive number")

        # Validate type-specific fields
        if recurrence_type == "weekly":
            days_of_week = recurrence_pattern.get("days_of_week")
            if days_of_week is not None:
                if not isinstance(days_of_week, list):
                    errors.append("days_of_week must be a list")
                else:
                    for day in days_of_week:
                        if not isinstance(day, int) or day < 0 or day > 6:
                            errors.append("days_of_week must contain integers between 0-6 (Sunday=0)")

        elif recurrence_type == "monthly":
            day_of_month = recurrence_pattern.get("day_of_month")
            if day_of_month is not None:
                if not isinstance(day_of_month, int) or day_of_month < 1 or day_of_month > 31:
                    errors.append("day_of_month must be an integer between 1-31")

        # Validate end condition if present
        end_condition = recurrence_pattern.get("end_condition")
        if end_condition:
            if not isinstance(end_condition, dict):
                errors.append("end_condition must be a dictionary")
            else:
                end_type = end_condition.get("type")
                valid_end_types = ["never", "after_n_occurrences", "by_date"]

                if end_type not in valid_end_types:
                    errors.append(f"Invalid end condition type '{end_type}'. Must be one of {valid_end_types}")

                if end_type == "after_n_occurrences":
                    value = end_condition.get("value")
                    if not isinstance(value, int) or value <= 0:
                        errors.append("end_condition.value must be a positive integer for 'after_n_occurrences'")

                elif end_type == "by_date":
                    value = end_condition.get("value")
                    if value is not None:
                        try:
                            from .datetime_utils import parse_iso_datetime
                            parse_iso_datetime(str(value))
                        except:
                            errors.append("end_condition.value must be a valid date for 'by_date'")

        return errors

    @staticmethod
    def get_next_occurrences_in_range(
        start_date: datetime,
        recurrence_pattern: Dict[str, Any],
        end_date: datetime
    ) -> List[datetime]:
        """
        Get all occurrences of a recurring task within a date range.

        Args:
            start_date: First occurrence date
            recurrence_pattern: Dictionary containing recurrence pattern details
            end_date: End date of the range

        Returns:
            List of occurrence dates within the range
        """
        occurrences = []
        current_date = start_date

        # Add the start date if it's within range
        if current_date <= end_date:
            occurrences.append(current_date)
        else:
            return occurrences  # Start date is already past the range

        # Continue calculating next occurrences
        while True:
            next_date = RecurrenceCalculator.calculate_next_occurrence(
                current_date,
                recurrence_pattern
            )

            if next_date is None or next_date > end_date:
                break

            occurrences.append(next_date)
            current_date = next_date

        return occurrences

    @staticmethod
    def get_occurrence_count(
        start_date: datetime,
        recurrence_pattern: Dict[str, Any],
        end_date: datetime
    ) -> int:
        """
        Count how many occurrences of a recurring task fall within a date range.

        Args:
            start_date: First occurrence date
            recurrence_pattern: Dictionary containing recurrence pattern details
            end_date: End date of the range

        Returns:
            Number of occurrences within the range
        """
        occurrences = RecurrenceCalculator.get_next_occurrences_in_range(
            start_date,
            recurrence_pattern,
            end_date
        )
        return len(occurrences)

    @staticmethod
    def is_date_matching_pattern(
        check_date: datetime,
        start_date: datetime,
        recurrence_pattern: Dict[str, Any]
    ) -> bool:
        """
        Check if a specific date matches the recurrence pattern from a start date.

        Args:
            check_date: Date to check
            start_date: First occurrence date
            recurrence_pattern: Dictionary containing recurrence pattern details

        Returns:
            True if the date matches the pattern, False otherwise
        """
        # If the check date is before the start date, it can't match
        if check_date.date() < start_date.date():
            return False

        # For daily recurrence
        if recurrence_pattern["type"] == "daily":
            interval = recurrence_pattern.get("interval", 1)
            diff_days = (check_date.date() - start_date.date()).days
            return diff_days % interval == 0

        # For weekly recurrence
        elif recurrence_pattern["type"] == "weekly":
            interval = recurrence_pattern.get("interval", 1)
            days_of_week = recurrence_pattern.get("days_of_week")

            # Check if the day of week matches
            if days_of_week and check_date.weekday() not in days_of_week:
                return False

            # Check if the interval matches
            if interval > 1:
                # Calculate how many weeks have passed since start
                diff_weeks = (check_date.date() - start_date.date()).days // 7
                return diff_weeks % interval == 0

            return True

        # For monthly recurrence
        elif recurrence_pattern["type"] == "monthly":
            # This is complex to validate retroactively, so we'll generate occurrences
            # up to the check date and see if it's in the list
            occurrences = RecurrenceCalculator.get_next_occurrences_in_range(
                start_date,
                recurrence_pattern,
                check_date
            )
            return check_date.date() in [occ.date() for occ in occurrences]

        # For custom recurrence (treated as daily)
        elif recurrence_pattern["type"] == "custom":
            interval = recurrence_pattern.get("interval", 1)
            diff_days = (check_date.date() - start_date.date()).days
            return diff_days % interval == 0

        return False


# Convenience functions
def calculate_next_occurrence(current_date: datetime, recurrence_pattern: Dict[str, Any]) -> Optional[datetime]:
    """Convenience function to calculate next occurrence."""
    return RecurrenceCalculator.calculate_next_occurrence(current_date, recurrence_pattern)


def calculate_all_occurrences(start_date: datetime, recurrence_pattern: Dict[str, Any], max_occurrences: int = 100) -> List[datetime]:
    """Convenience function to calculate all occurrences."""
    return RecurrenceCalculator.calculate_all_occurrences(start_date, recurrence_pattern, max_occurrences)


def validate_recurrence_pattern(recurrence_pattern: Dict[str, Any]) -> List[str]:
    """Convenience function to validate recurrence pattern."""
    return RecurrenceCalculator.validate_recurrence_pattern(recurrence_pattern)