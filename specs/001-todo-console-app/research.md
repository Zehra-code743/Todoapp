# Research & Technical Decisions: Todo Console App Phase I

**Feature**: 001-todo-console-app
**Date**: 2025-12-25
**Status**: Completed

## Overview

This document consolidates research findings and technical decisions for implementing the Phase I Todo Console Application. All decisions prioritize simplicity, spec-driven development, and alignment with the project constitution.

---

## Decision 1: Python Console I/O Pattern

**Decision**: Use standard `input()` and `print()` with UTF-8 encoding for console interaction

**Rationale**:
- Built-in Python functions meet all requirements (no external dependencies)
- Cross-platform support for Windows, Linux, Mac
- UTF-8 encoding handles special characters and emojis
- Simple error handling with try-except blocks
- No need for complex terminal libraries (curses, rich, etc.) for basic menu interface

**Alternatives Considered**:
- **curses library**: Rejected - too complex for basic menu, Windows compatibility issues
- **rich library**: Rejected - external dependency violates "standard library only" constraint
- **click library**: Rejected - external dependency, adds unnecessary framework overhead

**Implementation Notes**:
- Use `sys.stdout.encoding` check to verify UTF-8 support
- Wrap input/output in functions for consistent behavior
- Handle EOFError for Ctrl+D gracefully
- Handle KeyboardInterrupt (Ctrl+C) for graceful shutdown

---

## Decision 2: Task Storage Structure

**Decision**: Use Python list with dataclass objects for task storage

**Rationale**:
- `dataclasses` module (Python 3.7+) provides clean data structure with type hints
- List provides O(n) operations which meet performance requirements for 1000 tasks
- Auto-increment ID logic is trivial with list index or max(ids) + 1
- No need for complex data structures (dict, OrderedDict) for sequential access
- Dataclass supports validation, default values, and immutability options

**Alternatives Considered**:
- **Dict with ID keys**: Rejected - list is simpler, ID lookup is not primary access pattern
- **namedtuple**: Rejected - immutable, harder to update task fields
- **Plain dict**: Rejected - less type safety, no validation support, harder to maintain

**Implementation Notes**:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

---

## Decision 3: ID Generation Strategy

**Decision**: Auto-increment using `len(tasks) + 1` on creation, store permanently in Task object

**Rationale**:
- Simple and deterministic: first task is ID 1, second is ID 2, etc.
- No ID reuse even after deletion (IDs increment forever during session)
- Meets requirement "Task IDs remain unique and sequential throughout the session"
- Performance: O(1) operation to get next ID

**Alternatives Considered**:
- **max(task.id for task in tasks) + 1**: Rejected - O(n) operation, unnecessary when len() suffices
- **UUID**: Rejected - overkill for in-memory console app, not user-friendly for CLI input
- **Reuse deleted IDs**: Rejected - violates "sequential" requirement, adds complexity

**Implementation Notes**:
- Start ID counter at 1 (not 0) for user-friendliness
- Deletion does not affect ID sequence (gaps are acceptable)
- ID is immutable after creation (read-only field)

---

## Decision 4: Input Validation Strategy

**Decision**: Centralized validation functions with early-return pattern

**Rationale**:
- Reusable validation logic for title length (1-200), description length (≤1000)
- Clear error messages returned to caller
- Separation of concerns: validation logic separate from business logic
- Easy to test validation functions independently
- Follows Python convention: return tuple (is_valid, error_message)

**Alternatives Considered**:
- **Pydantic validation**: Rejected - external dependency
- **Inline validation**: Rejected - code duplication across operations (add, update)
- **Exception-based validation**: Rejected - exceptions for control flow is anti-pattern

**Implementation Pattern**:
```python
def validate_title(title: str) -> tuple[bool, str]:
    if not title or not title.strip():
        return False, "Title is required"
    if len(title) > 200:
        return False, "Title must be 1-200 characters"
    return True, ""

def validate_description(description: str) -> tuple[bool, str]:
    if len(description) > 1000:
        return False, "Description must be max 1000 characters"
    return True, ""
```

---

## Decision 5: Menu System Architecture

**Decision**: Function-based menu system with numbered options and dispatch dict

**Rationale**:
- Simple and extensible: each menu option maps to a function
- Easy to add new operations without modifying menu loop
- Clear separation between UI (menu) and business logic (operations)
- Follows single responsibility principle
- No need for OOP complexity (classes, inheritance)

**Alternatives Considered**:
- **Class-based menu system**: Rejected - unnecessary OOP overhead for simple menu
- **Command pattern**: Rejected - over-engineering for 5 operations
- **if-elif chain**: Rejected - less maintainable, harder to extend

**Implementation Pattern**:
```python
def main_menu():
    print("\nTodo Console App")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Mark Complete/Incomplete")
    print("4. Update Task")
    print("5. Delete Task")
    print("6. Exit")

def run():
    menu_actions = {
        "1": add_task,
        "2": view_tasks,
        "3": toggle_complete,
        "4": update_task,
        "5": delete_task,
        "6": exit_app
    }
    while True:
        main_menu()
        choice = input("Select option: ")
        action = menu_actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option, please try again")
```

---

## Decision 6: Error Handling Strategy

**Decision**: Try-except at input boundaries, explicit error messages, no stack traces shown to users

**Rationale**:
- Meets requirement "no stack traces shown to users"
- Graceful degradation: invalid input shows error, returns to menu
- Keyboard interrupt (Ctrl+C) caught at top level for clean exit
- EOF error (Ctrl+D) handled for unexpected input termination
- Business logic returns error messages as strings, not exceptions

**Alternatives Considered**:
- **Let exceptions propagate**: Rejected - would show stack traces to users
- **Exception hierarchy**: Rejected - overkill for simple console app
- **Logging framework**: Rejected - external dependency, unnecessary for console app

**Implementation Pattern**:
```python
def run():
    try:
        # Main application loop
        while True:
            main_menu()
            # ... menu logic
    except KeyboardInterrupt:
        print("\n\nApplication closed")
        sys.exit(0)
    except EOFError:
        print("\n\nInput terminated. Application closed")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred. Please restart the application.")
        sys.exit(1)
```

---

## Decision 7: Display Formatting Strategy

**Decision**: Use f-strings with manual column alignment for task table display

**Rationale**:
- Built-in f-strings meet requirements (no external dependencies)
- Manual padding with `str.ljust()` / `str.rjust()` provides clean columns
- UTF-8 symbols (○, ✓) for status indicators work cross-platform
- Simple enough to implement without table library
- Flexible for description truncation if needed

**Alternatives Considered**:
- **tabulate library**: Rejected - external dependency
- **PrettyTable library**: Rejected - external dependency
- **CSV-style output**: Rejected - less readable for users

**Implementation Pattern**:
```python
def format_task_table(tasks: list[Task]) -> str:
    if not tasks:
        return "No tasks yet"

    lines = []
    lines.append("ID | Status | Title                  | Description")
    lines.append("---|--------|------------------------|-------------")

    for task in tasks:
        status = "✓" if task.completed else "○"
        title = task.title[:20].ljust(20)  # Truncate and pad
        desc = (task.description or "—")[:30]
        lines.append(f"{task.id:2} | {status:^6} | {title} | {desc}")

    return "\n".join(lines)
```

---

## Decision 8: Testing Strategy

**Decision**: Use `pytest` with standard library mocking for unit tests

**Rationale**:
- pytest is industry standard, widely adopted
- Lightweight setup with minimal configuration
- Built-in `unittest.mock` for mocking user input (`input()`) and output (`print()`)
- Parametrized tests for validation logic
- Easy to run: `pytest` command with auto-discovery

**Alternatives Considered**:
- **unittest only**: Rejected - more verbose, less feature-rich than pytest
- **No testing**: Rejected - violates quality requirements, testing is essential
- **Manual testing only**: Rejected - not scalable, no regression detection

**Implementation Notes**:
- Test structure: `tests/unit/`, `tests/integration/`
- Mock `input()` to simulate user interactions
- Capture stdout to verify print output
- Test all validation functions with edge cases
- Test menu dispatch logic with invalid inputs

---

## Decision 9: Project Structure

**Decision**: Single project structure with `src/` and `tests/` directories

**Rationale**:
- Single console application (no frontend/backend split)
- Clear separation between source code and tests
- Follows Python packaging best practices
- Simple enough for Phase I, extensible for future phases

**Structure**:
```
src/
├── __init__.py
├── main.py          # Entry point, menu system
├── task.py          # Task dataclass
├── manager.py       # TaskManager class (CRUD operations)
└── ui.py            # Console I/O helpers, formatting

tests/
├── unit/
│   ├── test_task.py
│   ├── test_manager.py
│   └── test_validation.py
└── integration/
    └── test_full_workflow.py
```

**Alternatives Considered**:
- **Flat structure**: Rejected - doesn't scale, harder to organize
- **Feature-based structure**: Rejected - overkill for 5 operations
- **Monolithic single file**: Rejected - violates "max 30 lines per function" and clean code principles

---

## Decision 10: Package Management Setup (UV)

**Decision**: Use UV for project initialization, no runtime dependencies beyond stdlib

**Rationale**:
- UV is specified in requirements (project constraint)
- Fast, modern Python package manager
- Generates `pyproject.toml` for project metadata
- No `requirements.txt` needed (no external dependencies)
- Supports `uv run` for executing scripts

**Setup Commands**:
```bash
uv init todo-console
cd todo-console
uv add --dev pytest  # Development dependency only
uv run python src/main.py
```

**Alternatives Considered**:
- **pip + venv**: Rejected - UV is mandated by project requirements
- **poetry**: Rejected - not specified in project requirements
- **pipenv**: Rejected - not specified in project requirements

---

## Summary of Resolved Unknowns

All "NEEDS CLARIFICATION" items from Technical Context have been resolved:

| Item | Resolution |
|------|------------|
| **Testing Framework** | pytest with unittest.mock |
| **Console I/O Pattern** | Standard input()/print() with UTF-8 |
| **Data Structure** | List of dataclass objects |
| **ID Generation** | Auto-increment with len(tasks) + 1 |
| **Table Formatting** | Manual f-string formatting |
| **Error Handling** | Try-except at boundaries, explicit messages |
| **Menu Architecture** | Function-based dispatch with dict |

---

## Open Questions for Future Phases

These are intentionally deferred (out of scope for Phase I):

1. **Persistent Storage**: How will Phase II implement file/database persistence?
2. **Multi-user Support**: How will authentication and user isolation work in Phase III?
3. **Web Interface**: What frontend framework for Phase IV?
4. **AI Integration**: How will AI features integrate in Phase V?

---

## References

- **Python 3.13 Documentation**: https://docs.python.org/3.13/
- **Dataclasses Guide**: https://docs.python.org/3/library/dataclasses.html
- **pytest Documentation**: https://docs.pytest.org/
- **PEP 8 Style Guide**: https://peps.python.org/pep-0008/

---

**Research Complete**: 2025-12-25
**Next Phase**: Phase 1 - Data Model & Contracts
