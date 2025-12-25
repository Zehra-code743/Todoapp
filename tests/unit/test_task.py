"""Unit tests for Task dataclass and validation functions."""

import pytest
from datetime import datetime
from src.task import Task, validate_title, validate_description


class TestTaskDataclass:
    """Test Task dataclass creation and validation."""

    def test_create_task_with_valid_data(self):
        """Test creating a task with valid title and description."""
        task = Task(id=1, title="Buy groceries", description="Milk, eggs, bread")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_create_task_without_description(self):
        """Test creating a task with only title (description optional)."""
        task = Task(id=1, title="Call dentist")
        assert task.id == 1
        assert task.title == "Call dentist"
        assert task.description is None
        assert task.completed is False

    def test_create_task_with_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title is required"):
            Task(id=1, title="")

    def test_create_task_with_whitespace_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Title is required"):
            Task(id=1, title="   ")

    def test_create_task_with_title_too_long_raises_error(self):
        """Test that title longer than 200 chars raises ValueError."""
        long_title = "a" * 201
        with pytest.raises(ValueError, match="Title must be 1-200 characters"):
            Task(id=1, title=long_title)

    def test_create_task_with_description_too_long_raises_error(self):
        """Test that description longer than 1000 chars raises ValueError."""
        long_description = "a" * 1001
        with pytest.raises(ValueError, match="Description must be max 1000 characters"):
            Task(id=1, title="Valid title", description=long_description)

    def test_create_task_with_max_valid_title(self):
        """Test creating task with 200 char title (boundary test)."""
        max_title = "a" * 200
        task = Task(id=1, title=max_title)
        assert len(task.title) == 200

    def test_create_task_with_max_valid_description(self):
        """Test creating task with 1000 char description (boundary test)."""
        max_description = "a" * 1000
        task = Task(id=1, title="Title", description=max_description)
        assert len(task.description) == 1000


class TestValidateTitle:
    """Test validate_title helper function."""

    def test_valid_title(self):
        """Test validation of normal valid title."""
        is_valid, error = validate_title("Buy groceries")
        assert is_valid is True
        assert error == ""

    def test_empty_title(self):
        """Test validation of empty title."""
        is_valid, error = validate_title("")
        assert is_valid is False
        assert error == "Title is required"

    def test_whitespace_title(self):
        """Test validation of whitespace-only title."""
        is_valid, error = validate_title("   ")
        assert is_valid is False
        assert error == "Title is required"

    def test_title_too_long(self):
        """Test validation of title longer than 200 chars."""
        long_title = "a" * 201
        is_valid, error = validate_title(long_title)
        assert is_valid is False
        assert error == "Title must be 1-200 characters"

    def test_title_at_max_length(self):
        """Test validation of title exactly 200 chars."""
        max_title = "a" * 200
        is_valid, error = validate_title(max_title)
        assert is_valid is True
        assert error == ""


class TestValidateDescription:
    """Test validate_description helper function."""

    def test_valid_description(self):
        """Test validation of normal valid description."""
        is_valid, error = validate_description("Milk, eggs, bread")
        assert is_valid is True
        assert error == ""

    def test_empty_description(self):
        """Test validation of empty description (allowed)."""
        is_valid, error = validate_description("")
        assert is_valid is True
        assert error == ""

    def test_description_too_long(self):
        """Test validation of description longer than 1000 chars."""
        long_description = "a" * 1001
        is_valid, error = validate_description(long_description)
        assert is_valid is False
        assert error == "Description must be max 1000 characters"

    def test_description_at_max_length(self):
        """Test validation of description exactly 1000 chars."""
        max_description = "a" * 1000
        is_valid, error = validate_description(max_description)
        assert is_valid is True
        assert error == ""
