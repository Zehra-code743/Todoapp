"""Integration tests for complete user workflows."""

import pytest
from src.manager import TaskManager


class TestCreateTaskWorkflow:
    """Test complete create task user workflow."""

    def test_create_and_verify_task_workflow(self):
        """Test creating a task and verifying it was created correctly."""
        # Setup
        manager = TaskManager()

        # User Story 1: Create a task
        task, error = manager.create_task("Buy groceries", "Milk, eggs, bread")

        # Verify task was created
        assert error == ""
        assert task is not None
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False

        # Verify task is in manager's list
        assert len(manager.tasks) == 1
        assert manager.tasks[0] == task

    def test_create_multiple_tasks_workflow(self):
        """Test creating multiple tasks in sequence."""
        manager = TaskManager()

        # Create first task
        task1, error1 = manager.create_task("Task 1", "Description 1")
        assert error1 == ""
        assert task1.id == 1

        # Create second task
        task2, error2 = manager.create_task("Task 2", "Description 2")
        assert error2 == ""
        assert task2.id == 2

        # Create third task
        task3, error3 = manager.create_task("Task 3")
        assert error3 == ""
        assert task3.id == 3

        # Verify all tasks exist
        assert len(manager.tasks) == 3
        assert manager.tasks[0].title == "Task 1"
        assert manager.tasks[1].title == "Task 2"
        assert manager.tasks[2].title == "Task 3"

    def test_create_task_with_validation_error_workflow(self):
        """Test that validation errors don't affect subsequent operations."""
        manager = TaskManager()

        # Try to create task with invalid title
        task1, error1 = manager.create_task("")
        assert task1 is None
        assert error1 == "Title is required"
        assert len(manager.tasks) == 0

        # Create valid task after error
        task2, error2 = manager.create_task("Valid task")
        assert error2 == ""
        assert task2.id == 1  # ID should still start at 1
        assert len(manager.tasks) == 1


class TestViewTasksWorkflow:
    """Test complete view tasks user workflow."""

    def test_view_empty_task_list(self):
        """Test viewing tasks when list is empty."""
        manager = TaskManager()
        tasks = manager.get_all_tasks()
        assert tasks == []

    def test_view_tasks_after_creating_multiple(self):
        """Test viewing tasks after creating several."""
        manager = TaskManager()

        # Create tasks
        manager.create_task("Task 1", "Desc 1")
        manager.create_task("Task 2")
        manager.create_task("Task 3", "Desc 3")

        # View all tasks
        tasks = manager.get_all_tasks()
        assert len(tasks) == 3
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert tasks[2].title == "Task 3"
