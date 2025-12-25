# Data Model: Todo Console App Phase I

**Feature**: 001-todo-console-app
**Date**: 2025-12-25
**Status**: Approved

## Overview

This document defines the data model for the Phase I Todo Console Application. The model is designed for in-memory storage with clear validation rules and state transitions.

---

## Entity: Task

### Description
Represents a single todo item that a user wants to track. Each task has a unique identifier, descriptive content, completion status, and creation timestamp.

### Attributes

| Attribute | Type | Constraints | Default | Description |
|-----------|------|-------------|---------|-------------|
| `id` | `int` | Required, Unique, Read-only, > 0 | Auto-generated | Unique identifier, auto-incremented starting from 1 |
| `title` | `str` | Required, 1-200 chars | None | Short description of the task |
| `description` | `Optional[str]` | Optional, ≤1000 chars | `None` | Detailed description of the task |
| `completed` | `bool` | Required | `False` | Completion status (pending or completed) |
| `created_at` | `datetime` | Required, Read-only | `datetime.now()` | Timestamp when task was created |

### Validation Rules

**Title Validation**:
- MUST NOT be empty or whitespace-only
- MUST NOT be None
- MUST be between 1 and 200 characters (inclusive)
- Error message: "Title is required" (if empty), "Title must be 1-200 characters" (if too long)

**Description Validation**:
- MAY be None (optional field)
- If provided, MUST NOT exceed 1000 characters
- Error message: "Description must be max 1000 characters"

**ID Validation**:
- MUST be unique across all tasks in the session
- MUST be auto-generated (users cannot set manually)
- MUST be sequential (incremented for each new task)
- MUST be immutable after creation

**Completed Validation**:
- MUST be boolean (True or False)
- No string values allowed ("yes", "no", etc.)

**Created At Validation**:
- MUST be set automatically on task creation
- MUST be immutable after creation
- MUST use system local time (no timezone complexity for Phase I)

---

## State Transitions

### Task Lifecycle States

```
┌─────────────────────────────────────────────────────┐
│                   Task Created                      │
│               (completed = False)                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ├──────────── Toggle Complete ──────────┐
                  │                                       │
                  ▼                                       │
┌─────────────────────────────────────────────────────┐ │
│              Task Completed                         │ │
│               (completed = True)                    │ │
└─────────────────┬───────────────────────────────────┘ │
                  │                                       │
                  └──────────── Toggle Complete ──────────┘
                  │
                  ├──────────── Delete ────────────┐
                  │                                │
                  ▼                                ▼
┌─────────────────────────────────────────────────────┐
│              Task Deleted                           │
│          (removed from memory)                      │
└─────────────────────────────────────────────────────┘
```

### Allowed Operations by State

| Operation | Pending State | Completed State | Effect |
|-----------|---------------|-----------------|--------|
| **Create** | N/A | N/A | Creates new task in pending state |
| **View** | ✅ Allowed | ✅ Allowed | Displays task details, no state change |
| **Update (title/description)** | ✅ Allowed | ✅ Allowed | Updates fields, preserves completion status |
| **Toggle Complete** | ✅ Allowed | ✅ Allowed | Flips completed flag (pending ↔ completed) |
| **Delete** | ✅ Allowed | ✅ Allowed | Permanently removes task from memory |

---

## Data Structure (Python Implementation)

### Dataclass Definition

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique identifier (auto-generated, immutable)
        title: Short description (1-200 chars, required)
        description: Detailed description (≤1000 chars, optional)
        completed: Completion status (default: False)
        created_at: Creation timestamp (auto-generated, immutable)
    """
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate task fields after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Title is required")
        if len(self.title) > 200:
            raise ValueError("Title must be 1-200 characters")
        if self.description and len(self.description) > 1000:
            raise ValueError("Description must be max 1000 characters")
```

### Storage Structure

**In-Memory Storage**: List of Task objects

```python
# Global task storage (in TaskManager class)
tasks: list[Task] = []

# Example state after 3 tasks created:
tasks = [
    Task(id=1, title="Buy groceries", description="Milk, eggs", completed=False, created_at=...),
    Task(id=2, title="Call dentist", description=None, completed=True, created_at=...),
    Task(id=3, title="Finish report", description="Q4 summary", completed=False, created_at=...)
]
```

---

## Relationships

**Phase I**: No relationships between entities (single entity model)

**Future Phases** (out of scope):
- User → Task (one-to-many): Phase II/III multi-user support
- Task → Subtask (one-to-many): Phase IV hierarchical tasks
- Task → Tag (many-to-many): Phase IV categorization

---

## Operations & Constraints

### Create Task

**Inputs**:
- `title`: str (required, 1-200 chars)
- `description`: Optional[str] (≤1000 chars)

**Process**:
1. Validate title (length, non-empty)
2. Validate description (length if provided)
3. Generate next ID: `max(task.id for task in tasks) + 1` or `1` if empty
4. Create Task object with `completed=False`, `created_at=datetime.now()`
5. Append to tasks list

**Outputs**:
- Success: Task object with assigned ID
- Failure: Error message string

**Constraints**:
- ID must be unique and sequential
- Title is mandatory
- Description is optional

---

### View Tasks

**Inputs**: None

**Process**:
1. Check if tasks list is empty
2. If empty, return "No tasks yet"
3. If not empty, format each task into table row
4. Order by ID (oldest first)

**Outputs**:
- Formatted string (table view) or "No tasks yet"

**Constraints**:
- Tasks ordered by ID (oldest first)
- Status indicator: ○ (pending) or ✓ (completed)
- Empty description shows "—"

---

### Update Task

**Inputs**:
- `task_id`: int (required)
- `new_title`: Optional[str] (1-200 chars if provided)
- `new_description`: Optional[str] (≤1000 chars if provided)

**Process**:
1. Find task by ID
2. If not found, return error "Task not found: ID [N]"
3. Validate new title (if provided)
4. Validate new description (if provided)
5. Update only provided fields, preserve others
6. Return updated task

**Outputs**:
- Success: Updated Task object
- Failure: Error message string

**Constraints**:
- At least one field must be provided for update
- Original fields preserved if not updated
- ID and created_at are immutable

---

### Toggle Complete

**Inputs**:
- `task_id`: int (required)

**Process**:
1. Find task by ID
2. If not found, return error "Task not found: ID [N]"
3. Toggle `completed` field: `task.completed = not task.completed`
4. Return updated task

**Outputs**:
- Success: Updated Task object with new completion status
- Failure: Error message string

**Constraints**:
- Pending → Completed: `completed` changes from False to True
- Completed → Pending: `completed` changes from True to False

---

### Delete Task

**Inputs**:
- `task_id`: int (required)
- `confirmation`: bool (user must confirm)

**Process**:
1. Find task by ID
2. If not found, return error "Task not found: ID [N]"
3. Display task details for confirmation
4. If user confirms, remove from tasks list
5. If user cancels, return "Deletion cancelled"

**Outputs**:
- Success: Confirmation message with deleted task title
- Failure: Error message string or cancellation message

**Constraints**:
- Confirmation required before deletion
- Deletion is permanent (cannot undo)
- Deleted task ID is not reused

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Create Task | O(1) | Append to list |
| View All Tasks | O(n) | Iterate through all tasks |
| Find Task by ID | O(n) | Linear search through list |
| Update Task | O(n) | Find + update |
| Toggle Complete | O(n) | Find + toggle |
| Delete Task | O(n) | Find + remove |

### Space Complexity

- **Total**: O(n) where n = number of tasks
- **Per Task**: O(1) fixed size (no nested structures)

### Performance Requirements

- All operations MUST complete in < 100ms for up to 1000 tasks
- With O(n) operations and n ≤ 1000, performance requirements are easily met
- No optimization needed for Phase I (future: dict-based lookup if needed)

---

## Invariants

System-wide invariants that MUST always hold:

1. **Unique IDs**: No two tasks have the same ID
2. **Sequential IDs**: IDs increase monotonically (no gaps until deletion)
3. **Non-null IDs**: Every task has a valid ID > 0
4. **Title Presence**: Every task has a non-empty title
5. **Boolean Completed**: completed field is always True or False, never None
6. **Immutable ID**: Task ID never changes after creation
7. **Immutable Timestamp**: created_at never changes after creation

---

## Edge Cases & Handling

| Edge Case | Handling |
|-----------|----------|
| Empty title | Validation error: "Title is required" |
| Title > 200 chars | Validation error: "Title must be 1-200 characters" |
| Description > 1000 chars | Validation error: "Description must be max 1000 characters" |
| Non-existent ID | Error: "Task not found: ID [N]" |
| Empty task list | Display: "No tasks yet" |
| Delete last task | List becomes empty, next ID continues sequence |
| Special characters in title | Accepted (UTF-8 support) |
| Newlines in description | Accepted, displayed appropriately |

---

## Future Considerations (Out of Scope for Phase I)

These are intentionally deferred:

1. **Persistence**: How to serialize/deserialize Task objects to files/database
2. **User Association**: Adding `user_id` field for multi-user support
3. **Timestamps**: `updated_at`, `completed_at` for audit trails
4. **Soft Delete**: `deleted` flag instead of permanent removal
5. **Task Relationships**: Parent task, subtasks, dependencies
6. **Priority Field**: Adding priority levels (low, medium, high)
7. **Due Dates**: Adding `due_date` field for deadline tracking
8. **Tags/Categories**: Many-to-many relationship with Tag entity

---

**Model Version**: 1.0.0
**Last Updated**: 2025-12-25
**Next Phase**: Contracts & API Design
