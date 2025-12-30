# Todo App Phase 1 - QA Skills

**Project:** Todo Console Application (Python, In-Memory)
**Owner:** QA Agent
**Created:** 2025-12-27

## Overview

This directory contains specialized QA validation skills for the Todo App Phase 1 console application. Each skill is deterministic, reusable, and project-specific with concrete implementation details.

## Available Skills

### 1. **qa-validate-crud-operations.md**
Validates business logic in `TaskManager` class through comprehensive unit testing.

**Purpose:** Ensure CRUD operations (create, read, update, delete, toggle) work correctly with proper validation and error handling.

**When to Use:**
- Changes to `src/manager.py` or `src/task.py`
- Validation logic modifications
- Before commits affecting business logic
- User requests: "validate CRUD", "test task operations"

**Test Coverage:**
- 15+ unit tests for TaskManager methods
- Edge case validation (empty, whitespace, length limits)
- Error message contract verification
- ID auto-increment behavior
- State isolation between operations

**Key Validations:**
- ✓ Task creation with validation
- ✓ Task retrieval (all and by ID)
- ✓ Completion toggling
- ✓ Update operations
- ✓ Delete operations
- ✓ Error handling for invalid inputs
- ✓ Boundary condition tests

---

### 2. **qa-integration-test-workflow.md**
Validates end-to-end user workflows simulating real console usage patterns.

**Purpose:** Test complete user journeys where multiple CRUD operations are chained together, ensuring state consistency across operations.

**When to Use:**
- Multi-component changes
- Refactoring across multiple files
- Before releases or pull requests
- User requests: "test full workflow", "run integration tests"

**Test Coverage:**
- Create → View workflows
- Create → Toggle → View workflows
- Create → Update → View workflows
- Create → Delete → View workflows
- Multi-task complex scenarios
- Error recovery flows

**Key Validations:**
- ✓ State persistence across operations
- ✓ ID sequence integrity in multi-create
- ✓ Reference safety (task objects remain valid)
- ✓ Error isolation (failed ops don't corrupt state)
- ✓ Manager consistency checks

---

### 3. **qa-validate-ui-layer.md**
Validates presentation layer functions ensuring proper formatting, input handling, and separation from business logic.

**Purpose:** Test UI helper functions for correct display formatting, user input handling, and architectural separation.

**When to Use:**
- Changes to `src/ui.py` or `src/main.py`
- Console formatting modifications
- Error message display changes
- User requests: "test UI", "validate output", "check formatting"

**Test Coverage:**
- 22+ tests for UI components
- Table formatting with truncation
- Success/error message display
- Input handling and exception propagation
- Confirmation dialog logic
- UI/Logic separation validation

**Key Validations:**
- ✓ Task table formatting (headers, borders, alignment)
- ✓ Text truncation (titles 25 chars, descriptions 30 chars)
- ✓ Completion status symbols (✓ Done, ○ Pending)
- ✓ Message routing (errors to stderr)
- ✓ Color support and fallback
- ✓ Input exception propagation
- ✓ No business logic in UI layer

## Skill Structure

Each skill follows the standardized format:

1. **Purpose** - What it validates
2. **When to Use** - Specific triggers and scenarios
3. **Inputs** - Parameters and options
4. **Step-by-Step Process** - Detailed execution steps with commands
5. **Output** - Success and failure report formats
6. **Failure Handling** - Investigation and resolution steps
7. **Validation Checklist** - Completion criteria
8. **Dependencies** - Required files, tools, environment

## Usage Examples

### Run CRUD Validation
```bash
# Validate all TaskManager operations
uv run pytest tests/unit/test_manager.py -v

# Validate with coverage report
uv run pytest tests/unit/test_manager.py --cov=src.manager --cov-report=term-missing

# Test specific CRUD operation
uv run pytest tests/unit/test_manager.py::TestCreateTask -v
```

### Run Integration Tests
```bash
# Validate all workflows
uv run pytest tests/integration/test_full_workflow.py -v

# Test specific workflow
uv run pytest tests/integration/test_full_workflow.py::TestCreateTaskWorkflow -v

# Run with state consistency checks
uv run pytest tests/integration/ -v --tb=short
```

### Run UI Validation
```bash
# Validate all UI components
uv run pytest tests/unit/test_ui.py -v

# Test specific UI component
uv run pytest tests/unit/test_ui.py::TestFormatTaskTable -v

# Test with verbose output
uv run pytest tests/unit/test_ui.py -vv
```

### Run Full QA Suite
```bash
# Run all QA tests (unit + integration)
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run with fail-fast
uv run pytest tests/ -x
```

## Architecture Principles

### Test Layer Separation
- **Unit Tests** (`tests/unit/`) - Test individual functions/methods in isolation
- **Integration Tests** (`tests/integration/`) - Test workflows across components

### Test Isolation
- Each test creates own `TaskManager()` instance
- No shared state between tests
- Tests pass in any execution order

### Coverage Targets
- **src/manager.py**: ≥ 95% coverage
- **src/task.py**: ≥ 95% coverage
- **src/ui.py**: ≥ 90% coverage

### Error Handling Philosophy
- Tests validate both success and failure paths
- Error messages must match specification exactly
- Failed operations must not corrupt application state

## Project Context

**Phase 1 Constraints:**
- In-memory storage only (no database)
- Python console application (no web UI)
- UV tooling for dependency management
- Strict separation: `src/logic.py` vs `src/main.py`

**File Structure:**
```
D:\Todoapp\
├── src/
│   ├── main.py          # CLI entry point
│   ├── manager.py       # TaskManager (CRUD operations)
│   ├── task.py          # Task model and validators
│   └── ui.py            # UI helper functions
├── tests/
│   ├── unit/
│   │   ├── test_manager.py   # CRUD validation tests
│   │   ├── test_task.py      # Task model tests
│   │   └── test_ui.py        # UI layer tests
│   └── integration/
│       └── test_full_workflow.py  # Workflow tests
├── pyproject.toml       # Dependencies (pytest, pytest-cov)
└── .claude/
    └── skills/          # This directory
```

## Quality Gates

Before marking validation complete:

1. ✓ All tests pass (zero failures, zero errors)
2. ✓ Test execution time acceptable (< 10s total)
3. ✓ Coverage meets thresholds
4. ✓ No test isolation issues
5. ✓ Error messages match specification
6. ✓ Edge cases covered
7. ✓ Architectural separation maintained

## Related Documentation

- **Project Constitution**: `.specify/memory/constitution.md`
- **Phase 1 Spec**: `specs/phase-1/spec.md` (if exists)
- **Development Guide**: `CLAUDE.md`

## Skill Maintenance

**When to Update Skills:**
- New CRUD operations added to TaskManager
- New UI components added to console
- Test structure changes
- Coverage threshold changes
- New validation rules added to Task model

**Version Control:**
All skills include version history section tracking changes.

## Contact

**Skill Owner:** QA Agent
**Project:** Todo App Phase 1
**Last Updated:** 2025-12-27
