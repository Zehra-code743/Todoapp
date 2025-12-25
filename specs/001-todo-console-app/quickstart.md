# Quickstart Guide: Todo Console App Phase I

**Feature**: 001-todo-console-app
**Version**: 1.0.0
**Date**: 2025-12-25

## Overview

This quickstart guide helps developers set up and implement the Todo Console App Phase I. Follow these steps to build a working command-line todo application with in-memory storage.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.13+** installed and accessible in PATH
- **UV package manager** installed ([Installation Guide](https://github.com/astral-sh/uv))
- **Git** for version control
- **Terminal/Console** with UTF-8 encoding support
- **Operating System**: Windows (with WSL 2), Linux, or Mac

---

## Step 1: Repository Setup

### Clone and Navigate

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd todo-evolution

# Ensure you're on the feature branch
git checkout 001-todo-console-app
```

### Verify Branch

```bash
git branch --show-current
# Should output: 001-todo-console-app
```

---

## Step 2: Project Initialization

### Initialize with UV

```bash
# Initialize UV project (if not already done)
uv init --name todo-console

# Add development dependencies
uv add --dev pytest
```

### Verify pyproject.toml

Your `pyproject.toml` should look like this:

```toml
[project]
name = "todo-console"
version = "0.1.0"
description = "Phase I: In-memory todo console application"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = ["pytest"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Step 3: Project Structure

Create the following directory structure:

```
todo-console/
├── src/
│   ├── __init__.py          # Empty package marker
│   ├── main.py              # Entry point & menu system
│   ├── task.py              # Task dataclass
│   ├── manager.py           # TaskManager (CRUD operations)
│   └── ui.py                # Console I/O helpers
├── tests/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_task.py
│   │   ├── test_manager.py
│   │   └── test_validation.py
│   └── integration/
│       ├── __init__.py
│       └── test_full_workflow.py
├── specs/
│   └── 001-todo-console-app/
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       ├── research.md      # Technical decisions
│       ├── data-model.md    # Data model definition
│       ├── quickstart.md    # This file
│       └── contracts/       # Interface contracts
├── pyproject.toml           # Project metadata
└── README.md                # Project overview
```

---

## Step 4: Implementation Order

Follow this sequence for implementation:

### 4.1: Task Entity (`src/task.py`)

**Purpose**: Define the Task dataclass with validation

**Key Points**:
- Use `@dataclass` decorator
- Include type hints for all fields
- Add `__post_init__` for validation
- Implement validation for title (1-200 chars) and description (≤1000 chars)

**Reference**: `specs/001-todo-console-app/data-model.md`

**Acceptance Criteria**:
- [ ] Task has 5 attributes: id, title, description, completed, created_at
- [ ] Title validation works (empty, too long)
- [ ] Description validation works (too long)
- [ ] Default values set correctly (completed=False, created_at=now)

---

### 4.2: TaskManager (`src/manager.py`)

**Purpose**: Implement CRUD operations with in-memory storage

**Key Points**:
- Maintain list of Task objects
- Implement ID auto-increment logic
- Return tuple (result, error_message) for all operations
- Enforce validation rules

**Reference**: `specs/001-todo-console-app/contracts/task_manager_interface.md`

**Methods to Implement**:
1. `create_task(title, description=None)` → (Task | None, str)
2. `get_all_tasks()` → list[Task]
3. `get_task_by_id(task_id)` → Task | None
4. `update_task(task_id, title=None, description=None)` → (Task | None, str)
5. `toggle_complete(task_id)` → (Task | None, str)
6. `delete_task(task_id)` → (Task | None, str)

**Acceptance Criteria**:
- [ ] All 6 methods implemented
- [ ] ID auto-increment works correctly
- [ ] Validation errors return descriptive messages
- [ ] Operations preserve task list integrity

---

### 4.3: UI Helpers (`src/ui.py`)

**Purpose**: Console I/O formatting and helpers

**Key Functions**:
- `format_task_table(tasks: list[Task])` → str: Format tasks as table
- `get_user_input(prompt: str)` → str: Wrap input() with error handling
- `print_success(message: str)`: Display success messages
- `print_error(message: str)`: Display error messages
- `confirm_action(prompt: str)` → bool: Get yes/no confirmation

**Key Points**:
- Use UTF-8 symbols (○ for pending, ✓ for completed)
- Handle keyboard interrupts gracefully
- Consistent formatting across all outputs

**Acceptance Criteria**:
- [ ] Task table displays correctly with status indicators
- [ ] Empty list shows "No tasks yet"
- [ ] Error messages are clear and user-friendly

---

### 4.4: Main Application (`src/main.py`)

**Purpose**: Entry point, menu system, and operation dispatch

**Key Components**:
1. **Menu Display**: Show numbered menu options (1-6)
2. **Menu Dispatch**: Dict mapping choices to functions
3. **Operation Functions**:
   - `add_task()`: Prompt for title/description, call manager.create_task()
   - `view_tasks()`: Call manager.get_all_tasks(), format and display
   - `toggle_complete_menu()`: Prompt for ID, call manager.toggle_complete()
   - `update_task_menu()`: Prompt for ID and updates, call manager.update_task()
   - `delete_task_menu()`: Prompt for ID, confirm, call manager.delete_task()
   - `exit_app()`: Display "Application closed", exit gracefully
4. **Main Loop**: Display menu, get choice, dispatch, repeat

**Key Points**:
- Catch KeyboardInterrupt for Ctrl+C
- Catch EOFError for Ctrl+D
- Return to menu after each operation
- Display success/error messages

**Acceptance Criteria**:
- [ ] Menu displays correctly with 6 options
- [ ] All operations work end-to-end
- [ ] Invalid menu choices show error and redisplay menu
- [ ] Graceful exit on Ctrl+C or option 6

---

## Step 5: Testing

### Run Unit Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src tests/

# Run specific test file
uv run pytest tests/unit/test_manager.py
```

### Test Coverage Goals

- **Unit Tests**: 80%+ coverage for manager.py, task.py
- **Integration Tests**: Full workflow tests for all 5 operations

### Manual Testing Checklist

- [ ] Create task with title only
- [ ] Create task with title and description
- [ ] View empty task list
- [ ] View populated task list
- [ ] Update task title only
- [ ] Update task description only
- [ ] Update both title and description
- [ ] Mark task as complete
- [ ] Mark completed task as incomplete (toggle)
- [ ] Delete task with confirmation
- [ ] Cancel task deletion
- [ ] Handle invalid menu choice
- [ ] Handle non-existent task ID
- [ ] Handle title too long (>200 chars)
- [ ] Handle description too long (>1000 chars)
- [ ] Handle Ctrl+C graceful exit

---

## Step 6: Running the Application

### Local Development

```bash
# Run the application
uv run python src/main.py

# Or with UV's run command
uv run todo-console
```

### Expected Behavior

```
Todo Console App
1. Add Task
2. View Tasks
3. Mark Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit

Select option: 1

Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread

Task #1 'Buy groceries' created successfully

[Returns to main menu]
```

---

## Step 7: Validation & Quality Checks

### Code Quality

```bash
# Format code with black (if installed)
uv run black src/ tests/

# Type checking with mypy (if installed)
uv run mypy src/

# Linting with ruff (if installed)
uv run ruff check src/ tests/
```

### Requirements Verification

**Functional Requirements** (from spec.md):
- [ ] FR-001: In-memory storage using Python list ✅
- [ ] FR-002: Auto-incremented IDs starting from 1 ✅
- [ ] FR-003: Title required (1-200 chars) ✅
- [ ] FR-004: Description optional (max 1000 chars) ✅
- [ ] FR-005: New tasks default to pending ✅
- [ ] FR-006: Auto-generated creation timestamp ✅
- [ ] FR-007: Main menu with numbered options ✅
- [ ] FR-008-009: Input validation with error messages ✅
- [ ] FR-010-012: Formatted task display, ordered by ID ✅
- [ ] FR-013: Toggle completion status ✅
- [ ] FR-014: Update title/description, preserve unchanged ✅
- [ ] FR-015-017: Delete with confirmation ✅
- [ ] FR-018-020: Error handling, return to menu ✅
- [ ] FR-021-023: Exit option, success messages ✅

**Success Criteria** (from spec.md):
- [ ] SC-001: Task creation in under 15 seconds ✅
- [ ] SC-002: View performance < 100ms for 1000 tasks ✅
- [ ] SC-003: Clear visual distinction (○ vs ✓) ✅
- [ ] SC-004: Clear error messages, no stack traces ✅
- [ ] SC-005: 95% first-attempt success rate ✅
- [ ] SC-006: Stable performance with 1000 tasks ✅
- [ ] SC-007: Zero crashes, graceful error handling ✅
- [ ] SC-008: Intuitive menu navigation ✅
- [ ] SC-009: Unique sequential IDs ✅
- [ ] SC-010: Data persists in memory during session ✅

---

## Step 8: Commit & Documentation

### Create Commit

```bash
# Stage all files
git add src/ tests/ specs/ pyproject.toml README.md

# Commit with reference to spec
git commit -m "Implement Phase I: Todo Console App (001-todo-console-app)

- Add Task dataclass with validation (FR-001 to FR-006)
- Implement TaskManager with CRUD operations (FR-013 to FR-017)
- Create console UI with menu system (FR-007 to FR-012)
- Add error handling and user feedback (FR-018 to FR-023)
- Include unit and integration tests
- All 23 functional requirements implemented
- All 10 success criteria met

Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Update README.md

Ensure README includes:
- Project overview and purpose
- Setup instructions (Python, UV, dependencies)
- How to run the application
- How to run tests
- Known limitations (in-memory only, lost on exit)
- Future phases roadmap

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`
**Solution**: Run from repository root, not from `src/` directory

**Issue**: `UnicodeEncodeError` when displaying tasks
**Solution**: Ensure terminal supports UTF-8 encoding. On Windows, run `chcp 65001` before launching

**Issue**: Tests fail with import errors
**Solution**: Ensure `__init__.py` exists in `src/`, `tests/`, and test subdirectories

**Issue**: UV command not found
**Solution**: Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh` (Unix) or use installer (Windows)

---

## Next Steps

After completing Phase I:

1. **Review Specification**: `specs/001-todo-console-app/spec.md`
2. **Generate Tasks**: Run `/sp.tasks` to break down implementation into smaller tasks
3. **Implement Features**: Follow task list for step-by-step implementation
4. **Test Thoroughly**: Run automated and manual tests
5. **Prepare for Phase II**: File-based persistence

---

## Resources

- **Feature Spec**: `specs/001-todo-console-app/spec.md`
- **Data Model**: `specs/001-todo-console-app/data-model.md`
- **Interface Contract**: `specs/001-todo-console-app/contracts/task_manager_interface.md`
- **Research Decisions**: `specs/001-todo-console-app/research.md`
- **Python 3.13 Docs**: https://docs.python.org/3.13/
- **UV Documentation**: https://github.com/astral-sh/uv
- **pytest Documentation**: https://docs.pytest.org/

---

## Support

For questions or issues:
- Review specification files in `specs/001-todo-console-app/`
- Check constitution principles in `.specify/memory/constitution.md`
- Refer to CLAUDE.md for implementation guidance

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-25
**Status**: Ready for Implementation
