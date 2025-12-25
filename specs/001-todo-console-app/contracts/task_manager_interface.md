# TaskManager Interface Contract

**Feature**: 001-todo-console-app
**Version**: 1.0.0
**Date**: 2025-12-25

## Overview

This document defines the internal interface contract for the `TaskManager` class, which handles all CRUD operations for tasks. This interface serves as the contract between the UI layer (`main.py`, `ui.py`) and the business logic layer (`manager.py`).

---

## Class: TaskManager

### Responsibilities
- Manage in-memory task storage (list of Task objects)
- Provide CRUD operations with validation
- Generate unique sequential task IDs
- Enforce business rules and constraints

### Constructor

```python
class TaskManager:
    """
    Manages task storage and CRUD operations.

    Attributes:
        tasks (list[Task]): In-memory task storage
        next_id (int): Counter for next task ID
    """
    def __init__(self) -> None:
        """Initialize empty task manager."""
```

**Postconditions**:
- `tasks` list is empty
- `next_id` is initialized to 1

---

## Method Contracts

### 1. create_task

**Signature**:
```python
def create_task(self, title: str, description: str | None = None) -> tuple[Task | None, str]:
    """
    Create a new task with auto-generated ID.

    Args:
        title: Task title (1-200 characters, required)
        description: Task description (max 1000 characters, optional)

    Returns:
        tuple[Task | None, str]: (task, error_message)
            - On success: (Task object, "")
            - On failure: (None, error message string)

    Examples:
        >>> manager = TaskManager()
        >>> task, err = manager.create_task("Buy milk")
        >>> task.id
        1
        >>> task.title
        'Buy milk'
        >>> task.completed
        False
    """
```

**Preconditions**:
- `title` is a string (may be empty, validation will catch it)
- `description` is a string or None

**Postconditions** (on success):
- New Task object added to `tasks` list
- Task has unique ID = `next_id`
- `next_id` incremented by 1
- Task `completed` is False
- Task `created_at` is current timestamp

**Postconditions** (on failure):
- `tasks` list unchanged
- `next_id` unchanged
- Returns (None, error message)

**Error Cases**:
- Empty title → `(None, "Title is required")`
- Title > 200 chars → `(None, "Title must be 1-200 characters")`
- Description > 1000 chars → `(None, "Description must be max 1000 characters")`

---

### 2. get_all_tasks

**Signature**:
```python
def get_all_tasks(self) -> list[Task]:
    """
    Retrieve all tasks ordered by ID (oldest first).

    Returns:
        list[Task]: List of all tasks, ordered by ID

    Examples:
        >>> manager = TaskManager()
        >>> manager.create_task("Task 1")
        >>> manager.create_task("Task 2")
        >>> tasks = manager.get_all_tasks()
        >>> len(tasks)
        2
        >>> tasks[0].id
        1
    """
```

**Preconditions**: None

**Postconditions**:
- Returns copy of tasks list (or original if immutable assumed)
- Tasks ordered by ID ascending
- Empty list if no tasks exist

---

### 3. get_task_by_id

**Signature**:
```python
def get_task_by_id(self, task_id: int) -> Task | None:
    """
    Find task by ID.

    Args:
        task_id: Unique task identifier

    Returns:
        Task | None: Task object if found, None otherwise

    Examples:
        >>> manager = TaskManager()
        >>> task, _ = manager.create_task("Test")
        >>> found = manager.get_task_by_id(task.id)
        >>> found.title
        'Test'
        >>> manager.get_task_by_id(999)
        None
    """
```

**Preconditions**:
- `task_id` is an integer

**Postconditions**:
- Returns Task object if ID exists
- Returns None if ID doesn't exist
- No side effects (read-only operation)

---

### 4. update_task

**Signature**:
```python
def update_task(
    self,
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> tuple[Task | None, str]:
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

    Examples:
        >>> manager = TaskManager()
        >>> task, _ = manager.create_task("Old title", "Old desc")
        >>> updated, err = manager.update_task(task.id, title="New title")
        >>> updated.title
        'New title'
        >>> updated.description  # Preserved
        'Old desc'
    """
```

**Preconditions**:
- `task_id` is an integer
- At least one of `title` or `description` is provided

**Postconditions** (on success):
- Task found by ID has updated fields
- Unchanged fields preserved
- `id`, `completed`, `created_at` remain unchanged
- Returns (updated Task, "")

**Postconditions** (on failure):
- No changes to any task
- Returns (None, error message)

**Error Cases**:
- Task not found → `(None, "Task not found: ID [N]")`
- Invalid title → `(None, "Title must be 1-200 characters")`
- Invalid description → `(None, "Description must be max 1000 characters")`

---

### 5. toggle_complete

**Signature**:
```python
def toggle_complete(self, task_id: int) -> tuple[Task | None, str]:
    """
    Toggle task completion status (pending ↔ completed).

    Args:
        task_id: ID of task to toggle

    Returns:
        tuple[Task | None, str]: (task, error_message)
            - On success: (updated Task, "")
            - On failure: (None, error message)

    Examples:
        >>> manager = TaskManager()
        >>> task, _ = manager.create_task("Test")
        >>> task.completed
        False
        >>> toggled, _ = manager.toggle_complete(task.id)
        >>> toggled.completed
        True
        >>> toggled, _ = manager.toggle_complete(task.id)
        >>> toggled.completed
        False
    """
```

**Preconditions**:
- `task_id` is an integer

**Postconditions** (on success):
- Task `completed` field toggled (True ↔ False)
- All other fields unchanged
- Returns (updated Task, "")

**Postconditions** (on failure):
- No changes to any task
- Returns (None, error message)

**Error Cases**:
- Task not found → `(None, "Task not found: ID [N]")`

---

### 6. delete_task

**Signature**:
```python
def delete_task(self, task_id: int) -> tuple[Task | None, str]:
    """
    Delete task by ID (requires confirmation from caller).

    Args:
        task_id: ID of task to delete

    Returns:
        tuple[Task | None, str]: (deleted_task, error_message)
            - On success: (deleted Task object, "")
            - On failure: (None, error message)

    Examples:
        >>> manager = TaskManager()
        >>> task, _ = manager.create_task("To delete")
        >>> deleted, _ = manager.delete_task(task.id)
        >>> deleted.title
        'To delete'
        >>> manager.get_task_by_id(task.id)
        None
    """
```

**Preconditions**:
- `task_id` is an integer
- Caller has already obtained user confirmation

**Postconditions** (on success):
- Task removed from `tasks` list
- Returns (deleted Task object, "")
- `next_id` unchanged (no ID reuse)

**Postconditions** (on failure):
- No changes to `tasks` list
- Returns (None, error message)

**Error Cases**:
- Task not found → `(None, "Task not found: ID [N]")`

**Note**: This method does NOT handle user confirmation. The UI layer (`main.py`) is responsible for prompting the user and only calling this method after confirmation.

---

## Invariants

The `TaskManager` class MUST maintain these invariants:

1. **Unique IDs**: All tasks in `tasks` list have unique IDs
2. **Sequential IDs**: `next_id` is always greater than any existing task ID
3. **Non-negative IDs**: All task IDs are > 0
4. **Valid Tasks**: All tasks in `tasks` list pass validation rules
5. **List Integrity**: `tasks` list is never None (may be empty)

---

## Error Handling Strategy

All methods return `tuple[Result | None, str]`:
- **Success**: `(result_object, "")` - empty error string
- **Failure**: `(None, "error message")` - None result with descriptive error

This pattern allows callers to:
- Check for success with `if task:` or `if error:`
- Display error messages directly to users
- Avoid exception handling for business logic errors

---

## Threading & Concurrency

**Phase I**: No concurrency support required (single-threaded console app)

**Future Phases**: If multi-threading is needed, synchronization mechanisms (locks) must be added around list modifications.

---

## Usage Example

```python
from task_manager import TaskManager
from task import Task

# Initialize manager
manager = TaskManager()

# Create tasks
task1, err = manager.create_task("Buy groceries", "Milk, eggs, bread")
if err:
    print(f"Error: {err}")
else:
    print(f"Created task #{task1.id}: {task1.title}")

# View all tasks
tasks = manager.get_all_tasks()
for task in tasks:
    status = "✓" if task.completed else "○"
    print(f"{task.id} | {status} | {task.title}")

# Update task
updated, err = manager.update_task(task1.id, title="Buy groceries and supplies")
if err:
    print(f"Error: {err}")

# Toggle completion
toggled, err = manager.toggle_complete(task1.id)
if err:
    print(f"Error: {err}")
else:
    print(f"Task #{toggled.id} marked as {'completed' if toggled.completed else 'pending'}")

# Delete task (after confirmation in UI)
deleted, err = manager.delete_task(task1.id)
if err:
    print(f"Error: {err}")
else:
    print(f"Task #{deleted.id} '{deleted.title}' deleted")
```

---

**Contract Version**: 1.0.0
**Last Updated**: 2025-12-25
**Status**: Approved for Implementation
