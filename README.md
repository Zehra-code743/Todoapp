# Todo Console App - Phase I

A command-line todo application that stores tasks in memory. This is Phase I of a five-phase evolution toward a cloud-native AI-powered todo system.

## Features

- ✅ **Create Tasks**: Add tasks with title (required) and optional description
- ✅ **View Tasks**: See all tasks in a formatted table with status indicators (○ pending / ✓ completed)
- ✅ **Mark Complete**: Toggle task completion status
- ✅ **Update Tasks**: Modify task title and/or description
- ✅ **Delete Tasks**: Remove tasks with confirmation prompt

## Requirements

- **Python 3.13+** (currently running on Python 3.11.9)
- **UV Package Manager** - [Installation Guide](https://github.com/astral-sh/uv)
- **Terminal** with UTF-8 encoding support
- **Operating System**: Windows (WSL 2), Linux, or Mac

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Todoapp
```

### 2. Ensure You're on the Feature Branch

```bash
git checkout 001-todo-console-app
```

### 3. Install Dependencies

UV will automatically create a virtual environment and install dependencies:

```bash
uv sync
```

## Usage

### Running the Application

```bash
uv run python -m src.main
```

### Menu Options

```
Todo Console App
==================================================
1. Add Task
2. View Tasks
3. Mark Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit
==================================================
```

### Example Workflow

```bash
# Launch the app
uv run python -m src.main

# Select 1 to add a task
Select option: 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
✓ Task #1 'Buy groceries' created successfully

# Select 2 to view tasks
Select option: 2

================================================================================
ID   | Status   | Title                     | Description
--------------------------------------------------------------------------------
1    | ○ Pending | Buy groceries             | Milk, eggs, bread
================================================================================

# Select 3 to mark complete
Select option: 3
Enter task ID: 1
✓ Task #1 marked as completed

# Select 6 to exit
Select option: 6
Application closed. Goodbye!
```

## Testing

### Run All Tests

```bash
uv run pytest
```

### Run Tests with Coverage

```bash
uv run pytest --cov=src --cov-report=term
```

### Test Coverage

- **Task Entity**: 100% coverage (28/28 statements)
- **TaskManager**: 62% coverage (business logic tested)
- **Total**: 43 tests passing

## Project Structure

```
Todoapp/
├── src/
│   ├── __init__.py          # Package marker
│   ├── main.py              # Entry point & menu system
│   ├── task.py              # Task dataclass (100% coverage)
│   ├── manager.py           # TaskManager CRUD operations
│   └── ui.py                # Console I/O helpers
├── tests/
│   ├── unit/
│   │   ├── test_task.py     # Task entity tests (17 tests)
│   │   ├── test_manager.py  # Manager tests (21 tests)
│   │   └── test_ui.py       # UI helper tests (5 tests)
│   └── integration/
│       └── test_full_workflow.py  # End-to-end tests (5 tests)
├── specs/
│   └── 001-todo-console-app/
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       ├── tasks.md         # Task breakdown
│       └── ... (design docs)
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Known Limitations (Phase I)

- **In-Memory Only**: Tasks are stored in memory and lost when the application exits
- **Single User**: No authentication or multi-user support
- **No Persistence**: No file or database storage
- **No Due Dates**: Tasks don't have deadlines
- **No Priorities**: All tasks have equal priority
- **No Search/Filter**: Must view all tasks at once

These limitations are intentional for Phase I and will be addressed in future phases.

## Development

### Code Quality

- **Style Guide**: PEP 8
- **Type Hints**: All functions have type annotations
- **Docstrings**: All functions documented
- **Max Function Length**: 30 lines
- **No Global Variables**: Class or function scope only

### Architecture

- **Data Model**: `Task` dataclass with validation
- **Business Logic**: `TaskManager` class with CRUD operations
- **Presentation**: `ui.py` helper functions for console I/O
- **Entry Point**: `main.py` with menu system

## Troubleshooting

### ModuleNotFoundError: No module named 'src'

**Solution**: Run from repository root with module syntax:

```bash
cd D:/Todoapp
uv run python -m src.main
```

### UnicodeEncodeError

**Solution**: Ensure terminal supports UTF-8. On Windows, run:

```bash
chcp 65001
```

### UV command not found

**Solution**: Install UV:

```bash
# Unix/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Next Steps

- **Phase II**: File-based persistence
- **Phase III**: Database integration with multi-user support
- **Phase IV**: Web interface
- **Phase V**: AI-powered features

## License

This project is part of the Todo Evolution hackathon demonstrating spec-driven development with Claude Code.

## Contributing

This project follows strict spec-driven development:
1. All specifications in `/specs` directory
2. All code generated by Claude Code
3. No manual coding (AI-driven implementation)

For changes, update specifications first, then regenerate code.

---

**Version**: 1.0.0 (Phase I)
**Status**: ✅ Complete
**Last Updated**: 2025-12-25
