# QA Skill: Integration Test Workflow

**Owner:** QA Agent
**Project:** Todo App Phase 1 (Console)
**Version:** 1.0.0

## Purpose

Validates complete user workflows in the Todo Console App by running integration tests that simulate real user interactions across multiple operations. Ensures end-to-end functionality works correctly when CRUD operations are chained together, mimicking actual console usage patterns.

## When to Use

Trigger this skill when:
- Multiple components are modified in a single change (e.g., `src/manager.py` + `src/task.py`)
- Refactoring affects multiple CRUD operations
- Business logic changes that span across create → view → update → delete workflows
- Before releasing a new version or creating a pull request
- After fixing integration bugs or race conditions
- User requests: "test full workflow", "run integration tests", "validate end-to-end"

Do NOT use when:
- Only a single isolated method changed (use CRUD validation skill instead)
- Testing individual validation rules (use CRUD validation skill instead)
- UI-only changes with no business logic impact

## Inputs

| Input | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| workflow_scope | string | No | Specific workflow to test | `create`, `complete`, `full` |
| verbose | boolean | No | Show detailed test output | `true` (default: `false`) |
| fail_fast | boolean | No | Stop on first failure | `true` (default: `false`) |

## Step-by-Step Process

### Step 1: Environment Validation
**Action:** Verify integration test environment
```bash
uv run python -c "import pytest; from src.manager import TaskManager; from src.task import Task"
```

**Expected Output:** No import errors, all modules available

**Failure Condition:** If import fails, STOP and report:
- Missing module: "Integration tests require src/manager.py and src/task.py"
- Import error: Show specific missing dependency

---

### Step 2: Run Create Task Workflows
**Action:** Test complete task creation user journeys
```bash
uv run pytest tests/integration/test_full_workflow.py::TestCreateTaskWorkflow -v
```

**Expected Test Cases:**
1. `test_create_and_verify_task_workflow` - Single task creation with verification
2. `test_create_multiple_tasks_workflow` - Sequential task creation with ID auto-increment
3. `test_create_task_with_validation_error_workflow` - Error recovery and continuation

**Validation Checkpoints:**
- [ ] Task created with auto-generated ID
- [ ] Task appears in manager's list immediately
- [ ] Task attributes (title, description, completed) set correctly
- [ ] Multiple tasks maintain correct ID sequence (1, 2, 3...)
- [ ] Validation errors don't corrupt manager state
- [ ] Valid operations succeed after validation failures
- [ ] ID counter not incremented on failed creation

**Expected Output:**
```
tests/integration/test_full_workflow.py::TestCreateTaskWorkflow::test_create_and_verify_task_workflow PASSED
tests/integration/test_full_workflow.py::TestCreateTaskWorkflow::test_create_multiple_tasks_workflow PASSED
tests/integration/test_full_workflow.py::TestCreateTaskWorkflow::test_create_task_with_validation_error_workflow PASSED
========================= 3 passed in 0.XX s =========================
```

---

### Step 3: Run View Tasks Workflows
**Action:** Test task retrieval in various states
```bash
uv run pytest tests/integration/test_full_workflow.py::TestViewTasksWorkflow -v
```

**Expected Test Cases:**
1. `test_view_empty_task_list` - Empty list handling
2. `test_view_tasks_after_creating_multiple` - Multiple tasks display

**Validation Checkpoints:**
- [ ] Empty list returns `[]` without errors
- [ ] Tasks appear in creation order (by ID)
- [ ] All task attributes preserved correctly
- [ ] View operation doesn't modify task state

---

### Step 4: Run Complete Lifecycle Workflows
**Action:** Test full create → read → update → delete cycles
```bash
uv run pytest tests/integration/test_full_workflow.py -v --tb=short
```

**Expected Workflow Coverage:**
1. **Create → View Workflow:**
   - Create task → verify in list → confirm attributes

2. **Create → Toggle → View Workflow:**
   - Create task → mark complete → verify completed=True → mark incomplete → verify completed=False

3. **Create → Update → View Workflow:**
   - Create task → update title → verify change → update description → verify change

4. **Create → Delete → View Workflow:**
   - Create task → delete → verify removed from list → verify subsequent operations work

5. **Multi-Task Workflows:**
   - Create 3 tasks → toggle #2 → update #1 → delete #3 → verify final state

**Validation Checkpoints:**
- [ ] State changes persist across operations
- [ ] Task references remain valid after operations
- [ ] ID sequence maintained correctly
- [ ] Error in one operation doesn't affect others
- [ ] Manager state always consistent

---

### Step 5: Test Error Recovery Workflows
**Action:** Validate system resilience with error scenarios
```bash
uv run pytest tests/integration/test_full_workflow.py -k "error or invalid" -v
```

**Expected Scenarios:**
1. Failed create → successful create (ID counter correct)
2. Toggle non-existent task → no state corruption
3. Update non-existent task → no state corruption
4. Delete non-existent task → no state corruption

**Validation Checkpoints:**
- [ ] Failed operations return proper error messages
- [ ] Failed operations don't modify manager state
- [ ] Subsequent valid operations succeed
- [ ] Task list remains consistent after errors

---

### Step 6: Validate State Consistency
**Action:** Check manager state integrity after workflow execution
```bash
uv run python -c "
from src.manager import TaskManager

# Simulate workflow
manager = TaskManager()
task1, _ = manager.create_task('T1', 'D1')
task2, _ = manager.create_task('T2', 'D2')
manager.toggle_complete(task1.id)
manager.delete_task(task2.id)

# Validate final state
assert len(manager.tasks) == 1, 'Expected 1 task remaining'
assert manager.tasks[0].id == 1, 'Expected task #1 to remain'
assert manager.tasks[0].completed == True, 'Expected task #1 completed'
assert manager.next_id == 3, 'Expected next_id = 3'
print('✓ State consistency validated')
"
```

**Validation Checkpoints:**
- [ ] Task list length matches expected count
- [ ] Remaining tasks have correct attributes
- [ ] next_id reflects total tasks created (not current count)
- [ ] No memory leaks or orphaned references

---

### Step 7: Test Concurrent Operation Safety (Memory Model)
**Action:** Verify operations don't interfere with each other in single session
```bash
uv run python -c "
from src.manager import TaskManager

manager = TaskManager()

# Create tasks
t1, _ = manager.create_task('Task 1')
t2, _ = manager.create_task('Task 2')

# Modify via reference
t1.completed = True

# Verify change reflects in manager's list
assert manager.tasks[0].completed == True, 'Reference modification failed'

# Delete and verify references
manager.delete_task(t2.id)
assert len(manager.tasks) == 1, 'Delete failed'
assert t2.id == 2, 'Original reference should remain valid'

print('✓ Reference safety validated')
"
```

**Validation Checkpoints:**
- [ ] Task object references remain valid after modifications
- [ ] Changes via references reflect in manager's list
- [ ] Deleted tasks don't corrupt remaining references

## Output

### Success Output
```
✓ Integration Workflow Tests: PASSED

Workflow Coverage:
  ✓ Create Task Workflows (3 tests)
    • Single task creation with verification
    • Multiple tasks with ID sequencing
    • Error recovery and continuation

  ✓ View Tasks Workflows (2 tests)
    • Empty list handling
    • Multi-task retrieval

  ✓ Complete Lifecycle Workflows (5 scenarios)
    • Create → View
    • Create → Toggle → View
    • Create → Update → View
    • Create → Delete → View
    • Multi-task complex workflows

  ✓ Error Recovery (4 scenarios)
    • Failed operation state isolation
    • Non-existent task error handling
    • Validation error recovery

  ✓ State Consistency
    • Task list integrity maintained
    • ID counter correctness
    • Reference safety validated

Total Integration Tests: XX
  • Passed: XX
  • Failed: 0
  • Duration: 0.XX s

Status: All user workflows validated successfully
```

### Failure Output
```
✗ Integration Workflow Tests: FAILED

Failed Workflows: 2

1. TestCreateTaskWorkflow::test_create_multiple_tasks_workflow
   Location: tests/integration/test_full_workflow.py:30
   Failure: ID sequence broken

   Expected Task IDs: [1, 2, 3]
   Actual Task IDs:   [1, 2, 2]

   Root Cause: TaskManager.next_id not incremented in create_task()
   Affected File: src/manager.py:55
   Fix Required: Add self.next_id += 1 after task creation

2. State Consistency Check
   Failure: Task list corrupted after delete operation

   Expected: 1 task remaining (ID=1, completed=True)
   Actual:   0 tasks remaining

   Root Cause: delete_task() removing wrong task from list
   Affected File: src/manager.py:159
   Investigation: Check list.remove() logic with task references

Critical Issues:
  • ID Generation: Auto-increment broken for sequential creates
  • State Management: Task deletion affecting unrelated tasks

Impacted User Workflows:
  • Add multiple tasks (users will see duplicate IDs)
  • Delete task after marking complete (loses wrong task)

Action Required:
  1. Fix ID increment in src/manager.py:55
  2. Debug delete logic in src/manager.py:159
  3. Re-run: uv run pytest tests/integration/test_full_workflow.py -v
  4. Verify state consistency manually after fix
```

## Failure Handling

### Failure Type: Workflow State Corruption
**Symptom:** Integration test fails due to inconsistent manager state
**Example:** After create → toggle → delete, wrong task removed

**Investigation Steps:**
1. Run failing test with `-vv --tb=long` for full trace
2. Add print statements to show manager.tasks at each step
3. Check if object references vs IDs causing confusion
4. Verify in-memory list mutations are correct

**Resolution:**
```bash
# Run single failing workflow with verbose output
uv run pytest tests/integration/test_full_workflow.py::TestCreateTaskWorkflow::test_create_multiple_tasks_workflow -vv

# Add debug prints to investigate
uv run python -c "
from src.manager import TaskManager
manager = TaskManager()
t1, _ = manager.create_task('T1')
print(f'After T1: tasks={[t.id for t in manager.tasks]}, next_id={manager.next_id}')
t2, _ = manager.create_task('T2')
print(f'After T2: tasks={[t.id for t in manager.tasks]}, next_id={manager.next_id}')
"
```

**Report Format:**
- Exact workflow step where failure occurs
- Expected vs actual manager state (task count, IDs, attributes)
- Suspected code location: `src/manager.py:line_number`
- Recommend code review of specific method

**Retry:** No, requires code fix

---

### Failure Type: ID Sequence Broken
**Symptom:** Tasks have duplicate or incorrect IDs in multi-create workflows
**Root Causes:**
- `next_id` not incremented after successful create
- `next_id` incremented on failed create (validation error)

**Resolution:**
- Verify: `self.next_id += 1` happens ONLY after successful task creation
- Check: Line `src/manager.py:55` (after `self.tasks.append(task)`)
- Validate: ID counter not touched in error paths

**Report:**
```
ID Sequence Error detected in: test_create_multiple_tasks_workflow

Expected Sequence: Task #1, Task #2, Task #3
Actual Sequence:   Task #1, Task #2, Task #2

Code Location: src/manager.py:create_task()
Issue: self.next_id += 1 likely missing or in wrong location
```

**Retry:** No, requires code fix

---

### Failure Type: Reference vs Value Confusion
**Symptom:** Changes to task object don't reflect in manager's list or vice versa
**Root Cause:** Returning copies instead of references, or list management issues

**Investigation:**
```python
# Test reference behavior
manager = TaskManager()
task, _ = manager.create_task("Test")
task.completed = True
print(manager.tasks[0].completed)  # Should be True
```

**Resolution:**
- Verify Task objects are returned by reference, not copied
- Check that `get_task_by_id` returns actual list element
- Confirm no deep copying happening in methods

**Report:** "Reference safety issue: modifications via returned task don't affect manager's list"

**Retry:** No, requires architecture review

---

### Failure Type: Test Isolation Issues
**Symptom:** Tests pass individually but fail when run together
**Root Cause:** Tests sharing TaskManager instance or module-level state

**Resolution:**
- Each test should create own `manager = TaskManager()`
- Check for module-level variables in src/ files
- Verify no shared state between test classes

**Report:** "Test isolation violated: tests must be independent"

**Retry:** No, requires test refactoring

---

### Failure Type: Incomplete Workflow Coverage
**Symptom:** Some user workflows missing integration tests
**Examples:**
- No test for create → update → toggle → delete full cycle
- Missing test for batch operations

**Resolution:**
- Identify missing workflow: e.g., "Create → Update → Toggle → Verify"
- Document as gap, not failure
- Suggest new test case in issue tracker

**Report:**
```
Gap Detected: Missing integration test
Workflow: Create Task → Update Title → Mark Complete → Delete
Recommendation: Add test_complete_lifecycle_workflow() to test_full_workflow.py
Priority: Medium (covered by individual unit tests)
```

**Retry:** No, enhancement request

## Validation Checklist

Before marking this skill as complete:

- [ ] Integration test file exists: `tests/integration/test_full_workflow.py`
- [ ] All workflow test classes execute successfully
- [ ] Create → View workflow validated
- [ ] Create → Toggle → View workflow validated
- [ ] Multi-task workflows validated
- [ ] Error recovery scenarios tested
- [ ] State consistency checks pass
- [ ] Test execution time < 10 seconds
- [ ] No test isolation issues
- [ ] Output report includes workflow coverage matrix

## Dependencies

**Required Files:**
- `src/manager.py` - TaskManager implementation
- `src/task.py` - Task model
- `tests/integration/test_full_workflow.py` - Integration tests

**Required Tools:**
- `uv` - Python package manager
- `pytest>=9.0.2` - Test framework
- Python >= 3.11

**Environment:**
- Working directory: `D:\Todoapp\`
- Clean Python environment (no shared state)

## Related Skills

- `qa-validate-crud-operations.md` - For unit-level CRUD testing
- `qa-validate-ui-layer.md` - For UI workflow testing
- `code-review-integration.md` - Pre-test code review (Developer Agent)

## Notes

**Why Integration Tests Matter for Phase 1:**
Even though Phase 1 is in-memory only, integration tests catch:
- ID sequencing bugs in multi-create scenarios
- State corruption when operations are chained
- Reference vs value issues in Python data structures
- Error recovery flow problems

**Test Philosophy:**
Integration tests simulate actual console user behavior:
- User creates multiple tasks in a session
- User views, updates, completes, and deletes in sequence
- User encounters errors and continues working

**Performance Expectations:**
- All integration tests should complete in < 10 seconds
- If slower, indicates potential performance issue in business logic

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-27 | Initial skill creation for Todo App Phase 1 |
