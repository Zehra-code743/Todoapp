"""Unit tests for UI helper functions."""

import pytest
from src.ui import format_task_table
from src.task import Task
from datetime import datetime


class TestFormatTaskTable:
    """Test format_task_table function."""

    def test_format_empty_task_list(self):
        """Test formatting empty task list."""
        result = format_task_table([])
        assert result == "No tasks yet"

    def test_format_single_task_pending(self):
        """Test formatting single pending task."""
        task = Task(id=1, title="Buy groceries", description="Milk, eggs", completed=False)
        result = format_task_table([task])

        assert "1" in result
        assert "○" in result  # Pending indicator
        assert "Buy groceries" in result
        assert "Milk, eggs" in result

    def test_format_single_task_completed(self):
        """Test formatting single completed task."""
        task = Task(id=1, title="Call dentist", completed=True)
        result = format_task_table([task])

        assert "1" in result
        assert "✓" in result  # Completed indicator
        assert "Call dentist" in result

    def test_format_multiple_tasks_mixed_status(self):
        """Test formatting multiple tasks with mixed completion status."""
        tasks = [
            Task(id=1, title="Task 1", completed=False),
            Task(id=2, title="Task 2", completed=True),
            Task(id=3, title="Task 3", description="Desc 3", completed=False),
        ]
        result = format_task_table(tasks)

        # Verify all tasks are in output
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" in result

        # Verify status indicators
        assert "○" in result  # Pending
        assert "✓" in result  # Completed

        # Verify description handling
        assert "Desc 3" in result

    def test_format_task_without_description(self):
        """Test formatting task with no description."""
        task = Task(id=1, title="No description task")
        result = format_task_table([task])

        assert "No description task" in result
        assert ("—" in result or "(none)" in result.lower() or "No description task" in result)
