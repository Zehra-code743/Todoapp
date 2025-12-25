# Tasks: Todo In-Memory Python Console App (Phase I)

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included as this is a quality-focused project. All tests use pytest with unittest.mock.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project structure** (from plan.md): `src/`, `tests/` at repository root
- Source modules: `src/task.py`, `src/manager.py`, `src/ui.py`, `src/main.py`
- Test modules: `tests/unit/`, `tests/integration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Python console app structure

- [x] T001 Create project directory structure (src/, tests/unit/, tests/integration/)
- [x] T002 Initialize Python project with UV package manager (pyproject.toml)
- [x] T003 [P] Create empty __init__.py files in src/, tests/unit/, tests/integration/
- [x] T004 [P] Configure pytest as dev dependency in pyproject.toml
- [x] T005 [P] Create .gitignore for Python project (__pycache__, .pytest_cache, etc.)

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Task entity and shared utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create Task dataclass in src/task.py with all 5 attributes (id, title, description, completed, created_at)
- [x] T007 Add __post_init__ validation to Task dataclass (title 1-200 chars, description ≤1000 chars)
- [x] T008 [P] Create validation helper functions in src/task.py (validate_title, validate_description)
- [x] T009 [P] Create TaskManager class skeleton in src/manager.py with __init__ method
- [x] T010 [P] Create UI helper functions module src/ui.py (empty file, will add functions per story)
- [x] T011 Write unit tests for Task dataclass validation in tests/unit/test_task.py

**Checkpoint**: Foundation ready - Task entity exists, TaskManager initialized, user story implementation can now begin

---

## Phase 3: User Story 1 - Create a Task (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with title (required) and optional description. System generates unique ID and confirms creation.

**Independent Test**: Launch app, select "Add Task", enter title "Buy milk", verify task created with ID 1 and success message displayed

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T012 [P] [US1] Unit test for create_task method in tests/unit/test_manager.py
- [x] T013 [P] [US1] Unit test for create_task with empty title (error case) in tests/unit/test_manager.py
- [x] T014 [P] [US1] Unit test for create_task with title > 200 chars (error case) in tests/unit/test_manager.py
- [x] T015 [P] [US1] Unit test for create_task with description > 1000 chars (error case) in tests/unit/test_manager.py

### Implementation for User Story 1

- [x] T016 [US1] Implement TaskManager.create_task method in src/manager.py (validate, generate ID, append to list, return tuple)
- [x] T017 [US1] Implement get_user_input helper function in src/ui.py (wraps input() with error handling)
- [x] T018 [US1] Implement print_success and print_error functions in src/ui.py (colored output if supported)
- [x] T019 [US1] Create main.py with main_menu function displaying 6 menu options
- [x] T020 [US1] Implement add_task operation function in src/main.py (prompt for title/description, call manager.create_task, display result)
- [x] T021 [US1] Create main loop in src/main.py with menu dispatch dictionary mapping "1" → add_task
- [x] T022 [US1] Add error handling for KeyboardInterrupt (Ctrl+C) and EOFError (Ctrl+D) in main loop
- [x] T023 [US1] Integration test for create task workflow in tests/integration/test_full_workflow.py

**Checkpoint**: At this point, User Story 1 is fully functional - users can launch app and create tasks

---

## Phase 4: User Story 2 - View All Tasks (Priority: P2)

**Goal**: Users can see all tasks in a readable table format showing ID, title, status (○ pending / ✓ completed), and description

**Independent Test**: Create 3 tasks (2 pending, 1 completed), select "View Tasks", verify table displays all 3 with correct status indicators

### Tests for User Story 2

- [ ] T024 [P] [US2] Unit test for get_all_tasks method in tests/unit/test_manager.py
- [ ] T025 [P] [US2] Unit test for format_task_table with empty list in tests/unit/test_ui.py
- [ ] T026 [P] [US2] Unit test for format_task_table with mixed completed/pending tasks in tests/unit/test_ui.py

### Implementation for User Story 2

- [ ] T027 [US2] Implement TaskManager.get_all_tasks method in src/manager.py (return list ordered by ID)
- [ ] T028 [US2] Implement format_task_table function in src/ui.py (format tasks with UTF-8 symbols ○ ✓, handle empty list)
- [ ] T029 [US2] Implement view_tasks operation function in src/main.py (call manager.get_all_tasks, format, display)
- [ ] T030 [US2] Add view_tasks to menu dispatch dictionary in src/main.py (map "2" → view_tasks)
- [ ] T031 [US2] Integration test for view tasks workflow in tests/integration/test_full_workflow.py

**Checkpoint**: At this point, User Stories 1 AND 2 both work independently - users can create and view tasks

---

## Phase 5: User Story 3 - Mark Task as Complete/Incomplete (Priority: P3)

**Goal**: Users can toggle task completion status (pending ↔ completed) by entering task ID

**Independent Test**: Create task, mark as complete, verify status changes to completed; mark again, verify status toggles back to pending

### Tests for User Story 3

- [ ] T032 [P] [US3] Unit test for toggle_complete method (pending → completed) in tests/unit/test_manager.py
- [ ] T033 [P] [US3] Unit test for toggle_complete method (completed → pending) in tests/unit/test_manager.py
- [ ] T034 [P] [US3] Unit test for toggle_complete with non-existent ID (error case) in tests/unit/test_manager.py

### Implementation for User Story 3

- [ ] T035 [US3] Implement TaskManager.get_task_by_id method in src/manager.py (find task by ID, return Task or None)
- [ ] T036 [US3] Implement TaskManager.toggle_complete method in src/manager.py (find task, toggle completed flag, return tuple)
- [ ] T037 [US3] Implement toggle_complete_menu operation function in src/main.py (prompt for ID, call manager.toggle_complete, display result)
- [ ] T038 [US3] Add toggle_complete_menu to menu dispatch dictionary in src/main.py (map "3" → toggle_complete_menu)
- [ ] T039 [US3] Integration test for toggle complete workflow in tests/integration/test_full_workflow.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 all work independently - users can create, view, and mark tasks complete

---

## Phase 6: User Story 4 - Update Task Details (Priority: P4)

**Goal**: Users can modify task title and/or description by entering task ID and new values

**Independent Test**: Create task with title "Old", update title to "New", verify title changed; verify description preserved if not updated

### Tests for User Story 4

- [ ] T040 [P] [US4] Unit test for update_task (title only) in tests/unit/test_manager.py
- [ ] T041 [P] [US4] Unit test for update_task (description only) in tests/unit/test_manager.py
- [ ] T042 [P] [US4] Unit test for update_task (both fields) in tests/unit/test_manager.py
- [ ] T043 [P] [US4] Unit test for update_task with non-existent ID (error case) in tests/unit/test_manager.py
- [ ] T044 [P] [US4] Unit test for update_task with invalid title (error case) in tests/unit/test_manager.py

### Implementation for User Story 4

- [ ] T045 [US4] Implement TaskManager.update_task method in src/manager.py (find task, validate inputs, update fields, preserve unchanged, return tuple)
- [ ] T046 [US4] Implement update_task_menu operation function in src/main.py (prompt for ID, display current values, prompt for updates, call manager.update_task)
- [ ] T047 [US4] Add update_task_menu to menu dispatch dictionary in src/main.py (map "4" → update_task_menu)
- [ ] T048 [US4] Integration test for update task workflow in tests/integration/test_full_workflow.py

**Checkpoint**: At this point, User Stories 1-4 all work independently - users can create, view, mark complete, and update tasks

---

## Phase 7: User Story 5 - Delete a Task (Priority: P5)

**Goal**: Users can permanently remove a task by entering task ID and confirming deletion

**Independent Test**: Create task, delete with confirmation, verify task removed from list; test cancellation preserves task

### Tests for User Story 5

- [ ] T049 [P] [US5] Unit test for delete_task method in tests/unit/test_manager.py
- [ ] T050 [P] [US5] Unit test for delete_task with non-existent ID (error case) in tests/unit/test_manager.py
- [ ] T051 [P] [US5] Unit test for confirm_action helper (yes/no) in tests/unit/test_ui.py

### Implementation for User Story 5

- [ ] T052 [US5] Implement TaskManager.delete_task method in src/manager.py (find task, remove from list, return tuple with deleted task)
- [ ] T053 [US5] Implement confirm_action helper function in src/ui.py (prompt for yes/no, return boolean)
- [ ] T054 [US5] Implement delete_task_menu operation function in src/main.py (prompt for ID, display task, confirm, call manager.delete_task)
- [ ] T055 [US5] Add delete_task_menu to menu dispatch dictionary in src/main.py (map "5" → delete_task_menu)
- [ ] T056 [US5] Integration test for delete task workflow in tests/integration/test_full_workflow.py

**Checkpoint**: All 5 user stories are now independently functional - complete CRUD operations available

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final quality checks

- [ ] T057 [P] Implement exit_app operation function in src/main.py with graceful exit message
- [ ] T058 [P] Add exit_app to menu dispatch dictionary in src/main.py (map "6" → exit_app)
- [ ] T059 [P] Handle invalid menu choice (display error, re-display menu) in main loop
- [ ] T060 [P] Verify all functions have type hints per PEP 8 (review src/*.py)
- [ ] T061 [P] Verify all functions have docstrings (review src/*.py)
- [ ] T062 [P] Verify no functions exceed 30 lines (review src/*.py, refactor if needed)
- [ ] T063 [P] Run pytest with coverage flag, ensure 80%+ coverage for src/manager.py and src/task.py
- [ ] T064 Manual testing: Follow acceptance criteria checklist from quickstart.md (all 15 items)
- [ ] T065 Performance testing: Create 1000 tasks, verify view operation < 100ms
- [ ] T066 [P] Update README.md with setup instructions, usage guide, and known limitations
- [ ] T067 [P] Verify all 23 functional requirements (FR-001 to FR-023) are implemented
- [ ] T068 [P] Verify all 10 success criteria (SC-001 to SC-010) are met
- [ ] T069 Final validation: Run through all 5 user story workflows end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
  - ✅ Creates project structure and configuration
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
  - ✅ Creates Task entity, TaskManager skeleton, basic utilities
  - ⚠️ **CRITICAL**: No user story work until this phase completes
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - Can proceed in parallel if team capacity allows
  - Or sequentially in priority order: US1 → US2 → US3 → US4 → US5
  - Each story is independently testable
- **Polish (Phase 8)**: Depends on all user stories being complete
  - Final quality checks and cross-cutting improvements

### User Story Dependencies

- **User Story 1 (P1) - Create Task**: Can start after Foundational (Phase 2)
  - ✅ No dependencies on other user stories
  - ✅ MVP - First increment to deliver value
- **User Story 2 (P2) - View Tasks**: Can start after Foundational (Phase 2)
  - ✅ No dependencies on other user stories (can view empty list)
  - ⚠️ Best tested after US1 exists (to view created tasks)
- **User Story 3 (P3) - Toggle Complete**: Can start after Foundational (Phase 2)
  - ⚠️ Best tested after US1 and US2 (create task, toggle, view status change)
- **User Story 4 (P4) - Update Task**: Can start after Foundational (Phase 2)
  - ⚠️ Best tested after US1 and US2 (create task, update, view changes)
- **User Story 5 (P5) - Delete Task**: Can start after Foundational (Phase 2)
  - ⚠️ Best tested after US1 and US2 (create task, delete, verify removed from view)

### Within Each User Story

**Execution Order**:
1. Tests FIRST (write tests, ensure they FAIL before implementation)
2. Manager/Business logic (implement methods in src/manager.py)
3. UI helpers (implement display/input functions in src/ui.py)
4. Main application integration (wire up menu options in src/main.py)
5. Integration tests (end-to-end workflow validation)

**Sequential Dependencies**:
- Manager methods before UI integration
- UI helpers before main menu integration
- Implementation complete before integration tests pass

### Parallel Opportunities

**Within Setup Phase (Phase 1)**:
- T003, T004, T005 can all run in parallel (different files)

**Within Foundational Phase (Phase 2)**:
- T008, T009, T010 can run in parallel after T006-T007 complete (different files)

**Across User Stories (Phases 3-7)**:
- Once Foundational phase completes, ALL user stories can start in parallel
- Different team members can work on US1, US2, US3, US4, US5 simultaneously
- Each story delivers independent value

**Within Each User Story**:
- All unit tests marked [P] can run in parallel (same test file, different test methods)
- Example US1: T012, T013, T014, T015 can all run in parallel

**Within Polish Phase (Phase 8)**:
- T057, T058, T059, T060, T061, T062, T063, T066, T067, T068 can all run in parallel (different files/concerns)

---

## Parallel Execution Examples

### Example 1: Sequential MVP Delivery (Single Developer)

**Week 1**:
- Day 1-2: Phase 1 (Setup) + Phase 2 (Foundational)
- Day 3-4: Phase 3 (US1 - Create Task) ✅ **MVP Delivered**
- Day 5: Phase 4 (US2 - View Tasks)

**Week 2**:
- Day 1: Phase 5 (US3 - Toggle Complete)
- Day 2: Phase 6 (US4 - Update Task)
- Day 3: Phase 7 (US5 - Delete Task)
- Day 4-5: Phase 8 (Polish & Testing)

### Example 2: Parallel User Story Development (3 Developers)

**Week 1** (All developers):
- Day 1: Phase 1 (Setup) + Phase 2 (Foundational) - **Pair/mob programming**

**Week 1-2** (Parallel work after foundational phase):
- **Developer A**: Phase 3 (US1 - Create Task)
- **Developer B**: Phase 4 (US2 - View Tasks)
- **Developer C**: Phase 5 (US3 - Toggle Complete)

**Week 2** (Continue parallel):
- **Developer A**: Phase 6 (US4 - Update Task)
- **Developer B**: Phase 7 (US5 - Delete Task)
- **Developer C**: Phase 8 (Polish & Testing)

### Example 3: Test-Driven Parallel (2 Developers)

**Setup Phase** (Both):
- Phase 1 + Phase 2 together

**User Story 1 Parallel**:
- **Developer A**: T012-T015 (Write failing tests)
- **Developer B**: T016-T018 (Implement manager + UI helpers)
- Then swap: Developer A implements main.py (T019-T022), Developer B writes integration test (T023)

**Repeat pattern for US2-US5**

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Deliver First**:
- Phase 1 (Setup)
- Phase 2 (Foundational)
- Phase 3 (User Story 1 - Create Task) ✅

**Why This is MVP**:
- Users can launch app and create tasks
- Demonstrates core functionality
- Foundation for all other stories
- Can gather user feedback early

**Total Tasks for MVP**: T001-T023 (23 tasks)

### Incremental Delivery Plan

**Iteration 1 (MVP)**: US1 only
- Users can create tasks
- Deliverable: Working console app with task creation

**Iteration 2**: US1 + US2
- Users can create and view tasks
- Deliverable: Basic task tracking (input + output)

**Iteration 3**: US1 + US2 + US3
- Users can create, view, and mark tasks complete
- Deliverable: Full read-write cycle with status tracking

**Iteration 4**: US1 + US2 + US3 + US4
- Add update capability
- Deliverable: Complete CRUD except delete

**Iteration 5 (Full Feature Set)**: All 5 user stories
- Add delete capability
- Deliverable: Complete Phase I feature set

**Iteration 6 (Polish)**: Phase 8
- Final quality checks, documentation, performance testing
- Deliverable: Production-ready Phase I

### Recommended Approach

1. **Start with Setup + Foundational** (T001-T011)
   - Blocks everything else, must complete first
   - Estimated: 1-2 days

2. **Deliver MVP (US1)** (T012-T023)
   - Proves concept, demonstrates workflow
   - Estimated: 2-3 days

3. **Add US2 (View)** (T024-T031)
   - Completes input/output cycle
   - Estimated: 1-2 days

4. **Add US3, US4, US5 in sequence** (T032-T056)
   - Each adds independent capability
   - Estimated: 1-2 days each (3-6 days total)

5. **Polish & Validate** (T057-T069)
   - Final quality gates
   - Estimated: 2-3 days

**Total Estimated Timeline**: 10-16 days (single developer, sequential)
**Parallel Timeline** (3 developers): 6-10 days

---

## Validation Checklist

Before marking implementation complete, verify:

- ✅ All 69 tasks completed
- ✅ All 23 functional requirements (FR-001 to FR-023) implemented
- ✅ All 10 success criteria (SC-001 to SC-010) met
- ✅ All 5 user stories independently testable
- ✅ Unit test coverage ≥ 80% for src/manager.py and src/task.py
- ✅ All integration tests pass
- ✅ Manual testing checklist completed (quickstart.md)
- ✅ Code follows PEP 8 with type hints and docstrings
- ✅ No functions exceed 30 lines
- ✅ No global variables
- ✅ README.md complete with setup instructions
- ✅ Performance requirements met (< 100ms for 1000 tasks)

---

## Task Summary

**Total Tasks**: 69 tasks across 8 phases

**Task Breakdown by Phase**:
- Phase 1 (Setup): 5 tasks (T001-T005)
- Phase 2 (Foundational): 6 tasks (T006-T011)
- Phase 3 (US1): 12 tasks (T012-T023) - **4 tests + 7 implementation + 1 integration**
- Phase 4 (US2): 8 tasks (T024-T031) - **3 tests + 4 implementation + 1 integration**
- Phase 5 (US3): 8 tasks (T032-T039) - **3 tests + 4 implementation + 1 integration**
- Phase 6 (US4): 9 tasks (T040-T048) - **5 tests + 3 implementation + 1 integration**
- Phase 7 (US5): 8 tasks (T049-T056) - **3 tests + 3 implementation + 1 integration**
- Phase 8 (Polish): 13 tasks (T057-T069)

**Test Tasks**: 18 unit tests + 5 integration tests = 23 test tasks
**Implementation Tasks**: 46 implementation tasks

**Parallel Opportunities Identified**: 28 tasks marked [P] can run in parallel within their constraints

**MVP Scope**: 23 tasks (Phase 1 + Phase 2 + Phase 3/US1)

---

## Format Validation

✅ **All tasks follow checklist format**: `- [ ] [ID] [P?] [Story?] Description with file path`
✅ **All task IDs sequential**: T001 through T069
✅ **All user story tasks labeled**: [US1], [US2], [US3], [US4], [US5]
✅ **All parallel tasks marked**: [P] flag present where applicable
✅ **All tasks include file paths**: Exact paths specified in descriptions

---

**Tasks Generated**: 2025-12-25
**Ready for Implementation**: ✅ YES
**Next Step**: Begin Phase 1 (Setup) with T001-T005
