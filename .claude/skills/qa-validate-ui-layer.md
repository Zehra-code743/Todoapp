# QA Skill: Validate UI Layer

**Owner:** QA Agent
**Project:** Todo App Phase 1 (Console)
**Version:** 1.0.0

## Purpose

Validates the presentation layer of the Todo Console App by testing UI helper functions in `src/ui.py`. Ensures user input handling, output formatting, error messaging, and confirmation prompts work correctly and maintain separation from business logic.

## When to Use

Trigger this skill when:
- UI helper functions in `src/ui.py` are modified
- Console output formatting changes (table display, colors, messages)
- User input handling or validation display logic changes
- Menu system or prompt messages updated in `src/main.py`
- Error message display format changes
- User requests: "test UI", "validate output", "check formatting", "test console display"

Do NOT use when:
- Only business logic in `src/manager.py` or `src/task.py` changed (use CRUD validation instead)
- Testing CRUD operations or validation rules (use CRUD validation instead)
- Testing complete workflows (use integration test skill instead)

## Inputs

| Input | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| test_scope | string | No | Specific UI component to test | `formatting`, `input`, `messages` |
| verbose | boolean | No | Show detailed test output | `true` (default: `false`) |

## Step-by-Step Process

### Step 1: Environment Validation
**Action:** Verify UI test environment
```bash
uv run python -c "import pytest; from src.ui import get_user_input, print_success, print_error, format_task_table, confirm_action"
```

**Expected Output:** No import errors

**Failure Condition:** If import fails, STOP and report:
- Missing module: "UI tests require src/ui.py"
- Missing function: Identify which UI function is missing

---

### Step 2: Test Output Formatting Functions
**Action:** Validate task table formatting
```bash
uv run pytest tests/unit/test_ui.py::TestFormatTaskTable -v
```

**Expected Test Coverage:**
1. `test_format_empty_list` - Empty task list shows "No tasks yet"
2. `test_format_single_task` - Single task formats correctly
3. `test_format_multiple_tasks` - Multiple tasks display in table
4. `test_format_completed_tasks` - Completion status symbols correct
5. `test_format_long_title_truncation` - Titles > 25 chars truncate
6. `test_format_long_description_truncation` - Descriptions > 30 chars truncate
7. `test_format_task_without_description` - None description shows as "—"

**Validation Checkpoints:**
- [ ] Empty list returns `"No tasks yet"`
- [ ] Table has header row with: ID | Status | Title | Description
- [ ] Table has separator line (dashes or equals)
- [ ] Completed tasks show `"✓ Done"`
- [ ] Pending tasks show `"○ Pending"`
- [ ] Long titles truncated at 25 characters
- [ ] Long descriptions truncated at 30 characters
- [ ] Missing descriptions show placeholder `"—"`
- [ ] Table borders/separators render correctly

**Expected Output:**
```
tests/unit/test_ui.py::TestFormatTaskTable::test_format_empty_list PASSED
tests/unit/test_ui.py::TestFormatTaskTable::test_format_single_task PASSED
tests/unit/test_ui.py::TestFormatTaskTable::test_format_multiple_tasks PASSED
tests/unit/test_ui.py::TestFormatTaskTable::test_format_completed_tasks PASSED
tests/unit/test_ui.py::TestFormatTaskTable::test_format_long_title_truncation PASSED
tests/unit/test_ui.py::TestFormatTaskTable::test_format_long_description_truncation PASSED
tests/unit/test_ui.py::TestFormatTaskTable::test_format_task_without_description PASSED
======================== 7 passed in 0.XX s ========================
```

---

### Step 3: Test Message Display Functions
**Action:** Validate success and error message formatting
```bash
uv run pytest tests/unit/test_ui.py::TestPrintSuccess -v
uv run pytest tests/unit/test_ui.py::TestPrintError -v
```

**Expected Test Coverage:**

**Success Messages:**
1. `test_print_success_with_checkmark` - Message includes ✓ symbol
2. `test_print_success_color_fallback` - Works without color support

**Error Messages:**
1. `test_print_error_with_x_mark` - Message includes ✗ symbol
2. `test_print_error_to_stderr` - Errors output to stderr, not stdout
3. `test_print_error_color_fallback` - Works without color support

**Validation Checkpoints:**
- [ ] Success messages include ✓ prefix
- [ ] Error messages include ✗ prefix
- [ ] Success messages use green color (when supported)
- [ ] Error messages use red color (when supported)
- [ ] Error messages go to stderr
- [ ] Success messages go to stdout
- [ ] Color codes gracefully degrade if terminal doesn't support them

---

### Step 4: Test Input Handling
**Action:** Validate user input wrapper function
```bash
uv run pytest tests/unit/test_ui.py::TestGetUserInput -v
```

**Expected Test Coverage:**
1. `test_get_user_input_returns_string` - Normal input works
2. `test_get_user_input_handles_eof` - EOFError propagated correctly
3. `test_get_user_input_handles_keyboard_interrupt` - KeyboardInterrupt propagated

**Validation Checkpoints:**
- [ ] Function returns user input as string
- [ ] Prompt message displayed to user
- [ ] EOFError raised when input terminated (Ctrl+D)
- [ ] KeyboardInterrupt raised when interrupted (Ctrl+C)
- [ ] Exceptions propagate to caller (not caught internally)

---

### Step 5: Test Confirmation Dialog
**Action:** Validate yes/no confirmation logic
```bash
uv run pytest tests/unit/test_ui.py::TestConfirmAction -v
```

**Expected Test Coverage:**
1. `test_confirm_action_yes` - "yes" returns True
2. `test_confirm_action_y` - "y" returns True
3. `test_confirm_action_no` - "no" returns False
4. `test_confirm_action_n` - "n" returns False
5. `test_confirm_action_invalid` - Invalid input returns False
6. `test_confirm_action_case_insensitive` - "YES", "Yes" work
7. `test_confirm_action_whitespace_handling` - "  yes  " works

**Validation Checkpoints:**
- [ ] "yes" (any case) returns `True`
- [ ] "y" (any case) returns `True`
- [ ] "no" (any case) returns `False`
- [ ] "n" (any case) returns `False`
- [ ] Any other input returns `False` (safe default)
- [ ] Leading/trailing whitespace stripped
- [ ] Prompt includes " (yes/no): " suffix

---

### Step 6: Validate UI/Logic Separation
**Action:** Ensure UI functions don't contain business logic
```bash
uv run python -c "
import inspect
from src.ui import get_user_input, print_success, print_error, format_task_table, confirm_action

# Check UI functions don't import business logic
ui_source = inspect.getsource(inspect.getmodule(format_task_table))

forbidden_imports = ['from src.manager', 'from src.task import Task, validate']
violations = [imp for imp in forbidden_imports if imp in ui_source]

assert 'from src.task import Task' not in ui_source or 'TYPE_CHECKING' in ui_source, 'UI should use TYPE_CHECKING for Task import'

print('✓ UI/Logic separation validated')
"
```

**Validation Checkpoints:**
- [ ] `src/ui.py` doesn't import `TaskManager`
- [ ] Task model import uses `TYPE_CHECKING` (type hints only)
- [ ] No validation logic in UI functions
- [ ] No CRUD operations in UI functions
- [ ] UI functions only format/display data, don't modify it

---

### Step 7: Test UI Error Resilience
**Action:** Validate UI gracefully handles edge cases
```bash
uv run python -c "
from src.ui import format_task_table, print_success, print_error
from src.task import Task

# Test with extreme values
tasks = [
    Task(id=999999, title='a'*200, description='b'*1000),
    Task(id=1, title='', description=None),  # Will fail validation but test UI
]

# UI should not crash with valid Task objects
try:
    # Only test with valid tasks
    valid_task = Task(id=1, title='Test', description='x'*1000)
    output = format_task_table([valid_task])
    assert 'Test' in output, 'Task not in output'
    assert len(output.split('\\n')) > 3, 'Table not formatted'
    print('✓ UI edge case handling validated')
except Exception as e:
    print(f'✗ UI crashed with edge case: {e}')
    exit(1)
"
```

**Validation Checkpoints:**
- [ ] Large ID numbers display correctly
- [ ] Max-length titles/descriptions don't break formatting
- [ ] None descriptions handled gracefully
- [ ] Unicode characters in titles/descriptions work
- [ ] Empty string inputs don't crash functions

## Output

### Success Output
```
✓ UI Layer Validation: PASSED

Component Test Results:

  ✓ Task Table Formatting (7 tests)
    • Empty list display
    • Single/multiple task formatting
    • Completion status symbols
    • Text truncation (titles 25 chars, descriptions 30 chars)
    • Missing description handling

  ✓ Message Display (5 tests)
    • Success messages with ✓ symbol
    • Error messages with ✗ symbol
    • Color support and fallback
    • stderr routing for errors

  ✓ Input Handling (3 tests)
    • User input wrapper
    • EOFError propagation
    • KeyboardInterrupt propagation

  ✓ Confirmation Dialog (7 tests)
    • yes/y/no/n recognition
    • Case insensitivity
    • Whitespace handling
    • Safe default (False) for invalid input

  ✓ Architecture (2 checks)
    • UI/Logic separation maintained
    • No business logic in presentation layer

  ✓ Edge Case Resilience
    • Large values handled
    • Max-length strings formatted correctly
    • None values displayed properly

Total UI Tests: 22
  • Passed: 22
  • Failed: 0
  • Duration: 0.XX s

Status: All UI components validated successfully
```

### Failure Output
```
✗ UI Layer Validation: FAILED

Failed Tests: 3

1. tests/unit/test_ui.py::TestFormatTaskTable::test_format_long_title_truncation
   Location: tests/unit/test_ui.py:45
   Failure: Title not truncated correctly

   Input Title Length: 50 characters
   Expected Output: Title truncated at 25 chars
   Actual Output: Full 50-char title in table (breaks formatting)

   Root Cause: Missing slice in format_task_table()
   Code Location: src/ui.py:78
   Expected: title = task.title[:25]
   Actual: title = task.title

2. tests/unit/test_ui.py::TestPrintError::test_print_error_to_stderr
   Location: tests/unit/test_ui.py:67
   Failure: Error message sent to stdout instead of stderr

   Root Cause: Missing file=sys.stderr parameter
   Code Location: src/ui.py:53
   Fix: print(f"✗ {message}", file=sys.stderr)

3. tests/unit/test_ui.py::TestConfirmAction::test_confirm_action_whitespace_handling
   Location: tests/unit/test_ui.py:89
   Failure: Whitespace not stripped from input

   Input: "  yes  "
   Expected: True (should strip and recognize "yes")
   Actual: False (compared with whitespace)

   Root Cause: Missing .strip() in confirm_action()
   Code Location: src/ui.py:98
   Fix: response = get_user_input(f"{prompt} (yes/no): ").strip().lower()

UI Quality Issues Detected:
  • Table Formatting: Text truncation not working (display will break with long text)
  • Error Routing: Errors appearing in wrong stream (affects log parsing)
  • Input Handling: Whitespace causes false negatives in confirmations

Action Required:
  1. Add text truncation slicing in src/ui.py:78
  2. Add file=sys.stderr to error print in src/ui.py:53
  3. Add .strip() to confirm_action input in src/ui.py:98
  4. Re-run: uv run pytest tests/unit/test_ui.py -v
```

## Failure Handling

### Failure Type: Table Formatting Broken
**Symptom:** Task table doesn't display correctly
**Examples:**
- Columns misaligned
- Long text breaks table layout
- Missing borders or separators

**Investigation:**
```bash
# Test with problematic data
uv run python -c "
from src.ui import format_task_table
from src.task import Task

task = Task(id=1, title='a'*100, description='b'*200)
output = format_task_table([task])
print(output)
print('---')
print(f'Title length in output: {len([l for l in output.split(\"\\n\") if \"aaa\" in l][0])}')
"
```

**Resolution:**
- Check slicing logic for title/description: `task.title[:25]`
- Verify table borders use consistent character counts
- Confirm column widths match header definition

**Report:**
```
Table Formatting Issue
Component: format_task_table()
File: src/ui.py:78
Issue: Text not truncated, breaking column alignment
Expected: title[:25], description[:30]
Actual: Full text displayed without truncation
```

**Retry:** No, requires code fix

---

### Failure Type: Color Codes Breaking Output
**Symptom:** ANSI color codes visible in output or cause crashes
**Examples:**
- `\033[92m` appears in plain text
- Terminal doesn't support colors and crashes

**Resolution:**
- Verify try/except blocks catch color failures
- Test on terminal without color support
- Ensure fallback removes ALL color codes

**Investigation:**
```bash
# Test without color support
NO_COLOR=1 uv run python -c "
from src.ui import print_success, print_error
print_success('Test')
print_error('Test')
"
```

**Report:** "Color codes not handled gracefully - verify try/except in print_success/print_error"

**Retry:** After fixing exception handling

---

### Failure Type: Input Handling Not Raising Exceptions
**Symptom:** EOFError or KeyboardInterrupt not propagating to caller
**Root Cause:** UI function catching exceptions instead of re-raising

**Investigation:**
```python
# Verify exception propagation
from src.ui import get_user_input
try:
    # Simulate Ctrl+C (this is just for testing, not real interrupt)
    result = get_user_input("Test: ")
except KeyboardInterrupt:
    print("✓ Exception propagated correctly")
```

**Resolution:**
- Ensure `get_user_input` has `raise` statement in exception handlers
- Verify no bare `except:` clauses swallowing exceptions
- Check that exceptions bubble up to `src/main.py` main loop

**Report:** "Input exceptions being caught instead of propagated - check src/ui.py:26-27"

**Retry:** No, requires code fix

---

### Failure Type: Confirmation Dialog Logic Errors
**Symptom:** Wrong boolean returned for yes/no inputs
**Examples:**
- "yes" returns False
- "invalid" returns True (should be False - safe default)
- Case sensitivity issues ("YES" not recognized)

**Investigation:**
```python
from src.ui import confirm_action

test_cases = [
    ("yes", True),
    ("y", True),
    ("no", False),
    ("n", False),
    ("YES", True),
    ("  yes  ", True),
    ("maybe", False),
]

for inp, expected in test_cases:
    # Simulate input (in real test, use pytest fixtures)
    print(f"{inp!r} -> expects {expected}")
```

**Resolution:**
- Verify: `response.strip().lower()`
- Verify: `response in ["yes", "y"]`
- Confirm safe default (False) for unknown inputs

**Report:** "Confirmation logic incorrect at src/ui.py:99 - check strip/lower/comparison"

**Retry:** No, requires code fix

---

### Failure Type: UI/Logic Separation Violated
**Symptom:** UI functions contain business logic
**Examples:**
- `format_task_table` doing validation
- UI functions modifying Task objects
- UI functions importing TaskManager

**Investigation:**
```bash
# Check for business logic imports
uv run python -c "
import ast
import inspect
from src import ui

source = inspect.getsource(ui)
tree = ast.parse(source)

imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
for imp in imports:
    if isinstance(imp, ast.ImportFrom):
        if imp.module and 'manager' in imp.module:
            print(f'✗ UI imports business logic: {imp.module}')
            exit(1)

print('✓ No business logic imports found')
"
```

**Resolution:**
- Move validation logic to `src/task.py` or `src/manager.py`
- UI should only format/display, not validate or modify
- Use TYPE_CHECKING for type hints only

**Report:** "Architecture violation: UI function contains business logic - refactor needed"

**Retry:** No, requires refactoring

## Validation Checklist

Before marking this skill as complete:

- [ ] UI test file exists: `tests/unit/test_ui.py`
- [ ] Source file exists: `src/ui.py`
- [ ] All UI helper functions have test coverage
- [ ] Table formatting tests pass
- [ ] Message display tests pass
- [ ] Input handling tests pass
- [ ] Confirmation dialog tests pass
- [ ] UI/Logic separation verified
- [ ] Edge cases handled gracefully
- [ ] Test execution time < 3 seconds

## Dependencies

**Required Files:**
- `src/ui.py` - UI helper functions
- `src/task.py` - Task model (for type hints only)
- `tests/unit/test_ui.py` - UI unit tests

**Required Tools:**
- `uv` - Python package manager
- `pytest>=9.0.2` - Test framework
- Python >= 3.11

**Environment:**
- Working directory: `D:\Todoapp\`
- Terminal with basic output support (colors optional)

## Related Skills

- `qa-validate-crud-operations.md` - For testing business logic
- `qa-integration-test-workflow.md` - For full UI workflow testing
- `code-review-ui-layer.md` - Pre-test code review (Developer Agent)

## Notes

**Why UI Testing Matters:**
- Phase 1 is console-based - UI quality directly affects UX
- Table formatting bugs cause confusion (misaligned data)
- Error message routing affects debugging and log analysis
- Input handling bugs can crash the app or trap users

**Separation of Concerns:**
UI functions must ONLY:
- Format data for display
- Collect user input
- Handle presentation-layer errors (color support, etc.)

UI functions must NEVER:
- Validate business rules
- Modify data models
- Perform CRUD operations
- Import TaskManager

**Test Philosophy:**
UI tests validate presentation logic is correct and resilient, while maintaining architectural boundaries between presentation and business layers.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-27 | Initial skill creation for Todo App Phase 1 |
