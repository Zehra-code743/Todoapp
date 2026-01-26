"""
RecurrenceValidator for the Advanced Todo application.
Validates recurrence patterns according to the data model specification.
"""
from typing import List
from ..models.recurrence_pattern import RecurrencePattern, validate_recurrence_pattern


class RecurrenceValidator:
    """
    Service class for validating recurrence patterns.
    """

    @staticmethod
    def validate_pattern(recurrence_pattern_dict: dict) -> List[str]:
        """
        Validate a recurrence pattern dictionary.

        Args:
            recurrence_pattern_dict: Dictionary containing recurrence pattern

        Returns:
            List of validation errors (empty if valid)
        """
        try:
            # Create a RecurrencePattern instance to validate
            pattern = RecurrencePattern(**recurrence_pattern_dict)
            return validate_recurrence_pattern(pattern)
        except Exception as e:
            return [f"Invalid recurrence pattern format: {str(e)}"]

    @staticmethod
    def validate_daily_pattern(interval: int) -> List[str]:
        """
        Validate a daily recurrence pattern.

        Args:
            interval: Interval in days

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if interval <= 0:
            errors.append("Daily interval must be a positive integer")

        return errors

    @staticmethod
    def validate_weekly_pattern(
        interval: int,
        days_of_week: List[int] = None
    ) -> List[str]:
        """
        Validate a weekly recurrence pattern.

        Args:
            interval: Interval in weeks
            days_of_week: List of days [0-6] where 0 is Sunday

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if interval <= 0:
            errors.append("Weekly interval must be a positive integer")

        if days_of_week is not None:
            if not isinstance(days_of_week, list):
                errors.append("days_of_week must be a list")
            else:
                for day in days_of_week:
                    if not isinstance(day, int) or day < 0 or day > 6:
                        errors.append("days_of_week must contain integers between 0-6 (Sunday=0)")

        return errors

    @staticmethod
    def validate_monthly_pattern(
        interval: int,
        day_of_month: int = None
    ) -> List[str]:
        """
        Validate a monthly recurrence pattern.

        Args:
            interval: Interval in months
            day_of_month: Day of month (1-31)

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if interval <= 0:
            errors.append("Monthly interval must be a positive integer")

        if day_of_month is not None:
            if not isinstance(day_of_month, int) or day_of_month < 1 or day_of_month > 31:
                errors.append("day_of_month must be an integer between 1-31")

        return errors

    @staticmethod
    def validate_custom_pattern(interval: int) -> List[str]:
        """
        Validate a custom recurrence pattern.

        Args:
            interval: Interval in days

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if interval <= 0:
            errors.append("Custom interval must be a positive integer")

        return errors

    @staticmethod
    def validate_end_condition(end_condition: dict) -> List[str]:
        """
        Validate an end condition dictionary.

        Args:
            end_condition: End condition dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not isinstance(end_condition, dict):
            errors.append("End condition must be a dictionary")
            return errors

        end_type = end_condition.get("type")
        valid_end_types = ["never", "after_n_occurrences", "by_date"]

        if not end_type:
            errors.append("End condition must have a 'type' field")
        elif end_type not in valid_end_types:
            errors.append(f"Invalid end condition type '{end_type}'. Must be one of {valid_end_types}")

        if end_type == "after_n_occurrences":
            value = end_condition.get("value")
            if not isinstance(value, int) or value <= 0:
                errors.append("end_condition.value must be a positive integer for 'after_n_occurrences'")

        elif end_type == "by_date":
            value = end_condition.get("value")
            if value is not None:
                # Validate date format
                try:
                    from datetime import datetime
                    # Try to parse the date
                    if isinstance(value, str):
                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    errors.append("end_condition.value must be a valid date for 'by_date'")

        return errors

    @staticmethod
    def is_valid_pattern(recurrence_pattern_dict: dict) -> bool:
        """
        Check if a recurrence pattern is valid.

        Args:
            recurrence_pattern_dict: Dictionary containing recurrence pattern

        Returns:
            True if valid, False otherwise
        """
        return len(RecurrenceValidator.validate_pattern(recurrence_pattern_dict)) == 0

    @staticmethod
    def normalize_pattern(recurrence_pattern_dict: dict) -> dict:
        """
        Normalize a recurrence pattern dictionary to ensure consistent structure.

        Args:
            recurrence_pattern_dict: Dictionary containing recurrence pattern

        Returns:
            Normalized pattern dictionary
        """
        normalized = recurrence_pattern_dict.copy()

        # Ensure required fields have defaults
        if "interval" not in normalized:
            normalized["interval"] = 1

        # Ensure type is lowercase for consistency
        if "type" in normalized:
            normalized["type"] = normalized["type"].lower()

        # Validate and normalize days_of_week
        if "days_of_week" in normalized and normalized["days_of_week"] is not None:
            # Ensure it's a list and sort for consistency
            days = normalized["days_of_week"]
            if not isinstance(days, list):
                days = [days] if isinstance(days, int) else []
            # Remove duplicates and sort
            normalized["days_of_week"] = sorted(list(set(days)))

        # Validate day_of_month
        if "day_of_month" in normalized:
            day = normalized["day_of_month"]
            if day is not None and (not isinstance(day, int) or day < 1 or day > 31):
                # Reset invalid day_of_month
                normalized["day_of_month"] = None

        # Normalize end_condition
        if "end_condition" in normalized and normalized["end_condition"]:
            end_cond = normalized["end_condition"]
            if isinstance(end_cond, dict) and "type" in end_cond:
                end_cond["type"] = end_cond["type"].lower()

        return normalized