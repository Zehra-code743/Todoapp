"""TaskManager module for CRUD operations on tasks."""

from typing import Optional
from src.task import Task, validate_title, validate_description


class TaskManager:
    """
    Manages task storage and CRUD operations.

    Attributes:
        tasks: In-memory list of Task objects
        next_id: Counter for next task ID
    """

    def __init__(self) -> None:
        """Initialize empty task manager."""
        self.tasks: list[Task] = []
        self.next_id: int = 1

    def create_task(
        self, title: str, description: Optional[str] = None
    ) -> tuple[Optional[Task], str]:
        """
        Create a new task with auto-generated ID.

        Args:
            title: Task title (1-200 characters, required)
            description: Task description (max 1000 characters, optional)

        Returns:
            tuple[Task | None, str]: (task, error_message)
                - On success: (Task object, "")
                - On failure: (None, error message string)
        """
        # Validate title
        is_valid, error = validate_title(title)
        if not is_valid:
            return None, error

        # Validate description if provided
        if description:
            is_valid, error = validate_description(description)
            if not is_valid:
                return None, error

        # Create task with current next_id
        try:
            task = Task(
                id=self.next_id,
                title=title,
                description=description
            )
            self.tasks.append(task)
            self.next_id += 1
            return task, ""
        except ValueError as e:
            # Catch any validation errors from Task.__post_init__
            return None, str(e)

    def get_all_tasks(self) -> list[Task]:
        """
        Retrieve all tasks ordered by ID (oldest first).

        Returns:
            list[Task]: List of all tasks, ordered by ID
        """
        return self.tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Find task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task | None: Task object if found, None otherwise
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def toggle_complete(self, task_id: int) -> tuple[Optional[Task], str]:
        """
        Toggle task completion status (pending ↔ completed).

        Args:
            task_id: ID of task to toggle

        Returns:
            tuple[Task | None, str]: (task, error_message)
                - On success: (updated Task, "")
                - On failure: (None, error message)
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return None, f"Task not found: ID {task_id}"

        task.completed = not task.completed
        return task, ""

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> tuple[Optional[Task], str]:
        """
        Update task title and/or description.

        Args:
            task_id: ID of task to update
            title: New title (preserves existing if None)
            description: New description (preserves existing if None)

        Returns:
            tuple[Task | None, str]: (task, error_message)
                - On success: (updated Task, "")
                - On failure: (None, error message)
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return None, f"Task not found: ID {task_id}"

        # Validate and update title if provided
        if title is not None:
            is_valid, error = validate_title(title)
            if not is_valid:
                return None, error
            task.title = title

        # Validate and update description if provided
        if description is not None:
            is_valid, error = validate_description(description)
            if not is_valid:
                return None, error
            task.description = description

        return task, ""

    def delete_task(self, task_id: int) -> tuple[Optional[Task], str]:
        """
        Delete task by ID.

        Args:
            task_id: ID of task to delete

        Returns:
            tuple[Task | None, str]: (deleted_task, error_message)
                - On success: (deleted Task object, "")
                - On failure: (None, error message)
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return None, f"Task not found: ID {task_id}"

        self.tasks.remove(task)
        return task, ""
