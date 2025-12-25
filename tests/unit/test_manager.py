"""Unit tests for TaskManager CRUD operations."""

import pytest
from src.manager import TaskManager
from src.task import Task


class TestGetAllTasks:
    """Test TaskManager.get_all_tasks method."""

    def test_get_all_tasks_empty_list(self):
        """Test getting all tasks when list is empty."""
        manager = TaskManager()
        tasks = manager.get_all_tasks()

        assert tasks == []
        assert len(tasks) == 0

    def test_get_all_tasks_returns_all_tasks(self):
        """Test getting all tasks returns complete list."""
        manager = TaskManager()
        manager.create_task("Task 1")
        manager.create_task("Task 2")
        manager.create_task("Task 3")

        tasks = manager.get_all_tasks()

        assert len(tasks) == 3
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert tasks[2].title == "Task 3"

    def test_get_all_tasks_ordered_by_id(self):
        """Test that tasks are ordered by ID (oldest first)."""
        manager = TaskManager()
        task1, _ = manager.create_task("First")
        task2, _ = manager.create_task("Second")
        task3, _ = manager.create_task("Third")

        tasks = manager.get_all_tasks()

        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[2].id == 3


class TestGetTaskById:
    """Test TaskManager.get_task_by_id method."""

    def test_get_task_by_id_exists(self):
        """Test getting task that exists."""
        manager = TaskManager()
        created_task, _ = manager.create_task("Test task")

        found_task = manager.get_task_by_id(created_task.id)

        assert found_task is not None
        assert found_task.id == created_task.id
        assert found_task.title == "Test task"

    def test_get_task_by_id_not_exists(self):
        """Test getting task that doesn't exist."""
        manager = TaskManager()
        found_task = manager.get_task_by_id(999)

        assert found_task is None


class TestToggleComplete:
    """Test TaskManager.toggle_complete method."""

    def test_toggle_complete_pending_to_completed(self):
        """Test toggling task from pending to completed."""
        manager = TaskManager()
        task, _ = manager.create_task("Test task")
        assert task.completed is False

        toggled, error = manager.toggle_complete(task.id)

        assert error == ""
        assert toggled is not None
        assert toggled.completed is True

    def test_toggle_complete_completed_to_pending(self):
        """Test toggling task from completed back to pending."""
        manager = TaskManager()
        task, _ = manager.create_task("Test task")

        # Toggle to completed
        manager.toggle_complete(task.id)

        # Toggle back to pending
        toggled, error = manager.toggle_complete(task.id)

        assert error == ""
        assert toggled.completed is False

    def test_toggle_complete_non_existent_task(self):
        """Test toggling completion on non-existent task."""
        manager = TaskManager()
        toggled, error = manager.toggle_complete(999)

        assert toggled is None
        assert error == "Task not found: ID 999"


class TestCreateTask:
    """Test TaskManager.create_task method."""

    def test_create_task_with_title_and_description(self):
        """Test creating a task with title and description."""
        manager = TaskManager()
        task, error = manager.create_task("Buy groceries", "Milk, eggs, bread")

        assert error == ""
        assert task is not None
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False
        assert manager.next_id == 2
        assert len(manager.tasks) == 1

    def test_create_task_with_title_only(self):
        """Test creating a task with only title (description optional)."""
        manager = TaskManager()
        task, error = manager.create_task("Call dentist")

        assert error == ""
        assert task is not None
        assert task.id == 1
        assert task.title == "Call dentist"
        assert task.description is None
        assert task.completed is False

    def test_create_task_auto_increments_id(self):
        """Test that task IDs auto-increment correctly."""
        manager = TaskManager()

        task1, _ = manager.create_task("Task 1")
        task2, _ = manager.create_task("Task 2")
        task3, _ = manager.create_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
        assert manager.next_id == 4

    def test_create_task_with_empty_title_returns_error(self):
        """Test that empty title returns error."""
        manager = TaskManager()
        task, error = manager.create_task("")

        assert task is None
        assert error == "Title is required"
        assert len(manager.tasks) == 0
        assert manager.next_id == 1  # ID not incremented on failure

    def test_create_task_with_whitespace_title_returns_error(self):
        """Test that whitespace-only title returns error."""
        manager = TaskManager()
        task, error = manager.create_task("   ")

        assert task is None
        assert error == "Title is required"
        assert len(manager.tasks) == 0

    def test_create_task_with_title_too_long_returns_error(self):
        """Test that title longer than 200 chars returns error."""
        manager = TaskManager()
        long_title = "a" * 201
        task, error = manager.create_task(long_title)

        assert task is None
        assert error == "Title must be 1-200 characters"
        assert len(manager.tasks) == 0

    def test_create_task_with_description_too_long_returns_error(self):
        """Test that description longer than 1000 chars returns error."""
        manager = TaskManager()
        long_description = "a" * 1001
        task, error = manager.create_task("Valid title", long_description)

        assert task is None
        assert error == "Description must be max 1000 characters"
        assert len(manager.tasks) == 0

    def test_create_task_with_max_valid_lengths(self):
        """Test creating task with maximum valid lengths (boundary test)."""
        manager = TaskManager()
        max_title = "a" * 200
        max_description = "b" * 1000

        task, error = manager.create_task(max_title, max_description)

        assert error == ""
        assert task is not None
        assert len(task.title) == 200
        assert len(task.description) == 1000
