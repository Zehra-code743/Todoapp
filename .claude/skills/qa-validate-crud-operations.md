# QA Skill: Validate CRUD Operations

**Owner:** QA Agent
**Project:** Todo App Phase 1 (Console)
**Version:** 1.0.0

## Purpose

Validates all CRUD operations in the Todo Console App by running comprehensive unit tests against `TaskManager` methods. Ensures business logic in `src/manager.py` correctly handles task creation, reading, updating, deletion, and completion toggling with proper validation and error handling.

## When to Use

Trigger this skill when:
- New CRUD functionality is added to `src/manager.py`
- Validation logic is modified in `src/task.py` (title/description validators)
- Refactoring changes affect `TaskManager` class
- Before creating a commit with business logic changes
- After merging changes from other branches
- User requests: "validate CRUD", "test task operations", "run manager tests"

Do NOT use when:
- Only UI/presentation code in `src/main.py` or `src/ui.py` changed (use UI validation skill instead)
- Making documentation-only changes
- Modifying test files themselves

## Inputs

| Input | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| test_scope | string | No | Specific test class to run | `TestCreateTask` |
| verbose | boolean | No | Show detailed test output | `true` (default: `false`) |
| coverage | boolean | No | Generate coverage report | `true` (default: `false`) |

## Step-by-Step Process

### Step 1: Environment Validation
**Action:** Verify test environment is ready
```bash
uv run python -c "import pytest; import src.manager"
```

**Expected Output:** No import errors

**Failure Condition:** If import fails, STOP and report:
- Missing dependency: "Run `uv sync` to install pytest"
- Missing module: "Source file src/manager.py not found"

---

### Step 2: Run Unit Tests for TaskManager
**Action:** Execute all TaskManager unit tests
```bash
uv run pytest tests/unit/test_manager.py -v --tb=short
```

**Expected Output:**
```
tests/unit/test_manager.py::TestGetAllTasks::test_get_all_tasks_empty_list PASSED
tests/unit/test_manager.py::TestGetAllTasks::test_get_all_tasks_returns_all_tasks PASSED
tests/unit/test_manager.py::TestGetTaskById::test_get_task_by_id_exists PASSED
tests/unit/test_manager.py::TestGetTaskById::test_get_task_by_id_not_exists PASSED
tests/unit/test_manager.py::TestToggleComplete::test_toggle_complete_pending_to_completed PASSED
tests/unit/test_manager.py::TestToggleComplete::test_toggle_complete_completed_to_pending PASSED
tests/unit/test_manager.py::TestToggleComplete::test_toggle_complete_non_existent_task PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_with_title_and_description PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_with_title_only PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_auto_increments_id PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_with_empty_title_returns_error PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_with_whitespace_title_returns_error PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_with_title_too_long_returns_error PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_with_description_too_long_returns_error PASSED
tests/unit/test_manager.py::TestCreateTask::test_create_task_with_max_valid_lengths PASSED
===================== 15 passed in 0.XX s =====================
```

**Validation Checkpoints:**
- [ ] All `TestGetAllTasks` tests pass (3 tests)
- [ ] All `TestGetTaskById` tests pass (2 tests)
- [ ] All `TestToggleComplete` tests pass (3 tests)
- [ ] All `TestCreateTask` tests pass (10 tests)
- [ ] All `TestUpdateTask` tests pass (if present)
- [ ] All `TestDeleteTask` tests pass (if present)
- [ ] Zero test failures
- [ ] Zero test errors
- [ ] Test execution time < 5 seconds

---

### Step 3: Validate Edge Cases
**Action:** Check critical edge case coverage
```bash
uv run pytest tests/unit/test_manager.py -k "empty or whitespace or too_long or not_exists" -v
```

**Expected Coverage:**
- Empty title validation: `test_create_task_with_empty_title_returns_error`
- Whitespace title validation: `test_create_task_with_whitespace_title_returns_error`
- Title length limit: `test_create_task_with_title_too_long_returns_error`
- Description length limit: `test_create_task_with_description_too_long_returns_error`
- Non-existent task operations: `test_toggle_complete_non_existent_task`, `test_get_task_by_id_not_exists`
- Boundary tests: `test_create_task_with_max_valid_lengths`

**Failure Condition:** If any edge case test fails, report the specific validation rule that broke.

---

### Step 4: Verify Error Message Contracts
**Action:** Validate error messages match specification
```bash
uv run pytest tests/unit/test_manager.py -v --tb=long | grep -E "(Title is required|must be|not found)"
```

**Expected Error Messages (from spec):**
- `"Title is required"` - for empty/whitespace titles
- `"Title must be 1-200 characters"` - for titles > 200 chars
- `"Description must be max 1000 characters"` - for descriptions > 1000 chars
- `"Task not found: ID {id}"` - for non-existent task operations

**Failure Condition:** If error messages don't match spec exactly, flag as contract violation.

---

### Step 5: Coverage Report (Optional)
**Action:** Generate coverage report if requested
```bash
uv run pytest tests/unit/test_manager.py --cov=src.manager --cov-report=term-missing
```

**Expected Coverage:** ≥ 95% for `src/manager.py`

**Report Format:**
```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
src/manager.py        XX      X    XX%    XX-XX
```

---

### Step 6: Validate Test Isolation
**Action:** Run tests in random order to ensure no state leakage
```bash
uv run pytest tests/unit/test_manager.py --random-order
```

**Expected:** All tests pass regardless of execution order (no shared state between tests)

**Failure Condition:** If tests fail in random order but pass normally, report test isolation issue.

## Output

### Success Output
```
✓ CRUD Operations Validation: PASSED

Test Results:
  • Total Tests: 15
  • Passed: 15
  • Failed: 0
  • Skipped: 0
  • Duration: 0.XX s

Critical Validations:
  ✓ Task creation with validation
  ✓ Task retrieval (all and by ID)
  ✓ Task completion toggling
  ✓ Task update operations
  ✓ Task deletion
  ✓ Error handling for invalid inputs
  ✓ Error handling for non-existent tasks
  ✓ ID auto-increment behavior
  ✓ Boundary condition tests

Coverage: XX% (src/manager.py)
Status: All CRUD operations validated successfully
```

### Failure Output
```
✗ CRUD Operations Validation: FAILED

Failed Tests: X
  1. tests/unit/test_manager.py::TestCreateTask::test_create_task_with_empty_title_returns_error
     Expected: task=None, error="Title is required"
     Actual: task=Task(id=1,...), error=""
     Root Cause: validate_title() not called in create_task()

  2. tests/unit/test_manager.py::TestToggleComplete::test_toggle_complete_non_existent_task
     Expected: error="Task not found: ID 999"
     Actual: error="Task not found with id: 999"
     Root Cause: Error message format mismatch

Impacted Operations:
  • Task Creation (validation bypassed)
  • Error Messaging (spec contract violated)

Action Required:
  1. Fix validation logic in src/manager.py:23-45
  2. Update error message in src/manager.py:99
  3. Re-run: uv run pytest tests/unit/test_manager.py -v
```

## Failure Handling

### Failure Type: Import Error
**Symptom:** `ModuleNotFoundError: No module named 'pytest'`
**Resolution:**
```bash
uv sync
uv run pytest --version
```
**Retry:** Yes, after successful sync

---

### Failure Type: Test Failures (Validation Logic)
**Symptom:** Assertions fail in validation tests
**Root Cause Analysis:**
1. Check if `validate_title()` or `validate_description()` logic changed
2. Verify `TaskManager.create_task()` calls validators correctly
3. Compare error messages against spec requirements

**Resolution:**
- Report exact test name and line number: `tests/unit/test_manager.py:152`
- Show expected vs actual values
- Provide code reference to broken logic: `src/manager.py:37-39`
- DO NOT fix automatically - report to developer with context

**Retry:** No, requires code fix first

---

### Failure Type: Test Failures (Business Logic)
**Symptom:** CRUD operations return incorrect results
**Investigation Steps:**
1. Check if in-memory `self.tasks` list is correctly managed
2. Verify `self.next_id` increments only on success
3. Confirm task objects are not mutated unexpectedly

**Resolution:**
- Run single failing test in verbose mode: `uv run pytest tests/unit/test_manager.py::TestCreateTask::test_create_task_auto_increments_id -vv`
- Capture actual vs expected state
- Report to developer with test isolation details

**Retry:** No, requires code fix first

---

### Failure Type: Test Isolation Issues
**Symptom:** Tests pass normally but fail with `--random-order`
**Root Cause:** Tests sharing state via `TaskManager` instance or module-level variables

**Resolution:**
- Identify which test pair conflicts
- Check for missing test setup/teardown
- Verify each test creates its own `TaskManager()` instance
- Report: "Test isolation violated: [test_name_1] affects [test_name_2]"

**Retry:** No, requires test refactoring

---

### Failure Type: Coverage Below Threshold
**Symptom:** Coverage < 95% for `src/manager.py`
**Resolution:**
- Report uncovered lines: `Missing: 45-47, 89`
- Identify missing test scenarios
- Suggest specific test cases needed
- DO NOT block validation - report as warning only

**Retry:** No, coverage improvement is enhancement

## Validation Checklist

Before marking this skill as complete, verify:

- [ ] Test file exists: `tests/unit/test_manager.py`
- [ ] Source file exists: `src/manager.py`
- [ ] pytest is installed and importable
- [ ] All CRUD methods have corresponding test classes
- [ ] Edge case tests exist and pass
- [ ] Error messages match specification
- [ ] Test execution time < 5 seconds
- [ ] No test isolation issues detected
- [ ] Coverage report generated (if requested)
- [ ] Output report includes pass/fail count, duration, and validation summary

## Dependencies

**Required Files:**
- `src/manager.py` - TaskManager implementation
- `src/task.py` - Task model and validators
- `tests/unit/test_manager.py` - Unit tests
- `pyproject.toml` - Contains pytest dev dependency

**Required Tools:**
- `uv` - Python package manager
- `pytest>=9.0.2` - Test framework
- `pytest-cov>=7.0.0` - Coverage plugin (optional)
- `pytest-random-order` - Test isolation validation (optional)

**Environment:**
- Python >= 3.11
- Working directory: `D:\Todoapp\`

## Related Skills

- `qa-validate-ui-layer.md` - For testing UI/presentation logic
- `qa-integration-test-workflow.md` - For end-to-end workflow validation
- `code-review-business-logic.md` - For pre-test code review (Developer Agent)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-27 | Initial skill creation for Todo App Phase 1 |
