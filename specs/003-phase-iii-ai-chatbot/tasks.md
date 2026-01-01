---
description: "Implementation tasks for Phase III - Todo AI Chatbot"
---

# Tasks: Phase III - Todo AI Chatbot

**Input**: Design documents from `/specs/003-phase-iii-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included for critical integration points and contract validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` directory
- **Frontend**: `frontend/src/` directory
- **Tests**: `backend/tests/` and `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment configuration and dependency installation

- [x] T001 Install backend dependencies: openai, mcp, structlog in backend/requirements.txt
- [x] T002 Install frontend dependency: @openai/chatkit in frontend/package.json
- [x] T003 [P] Add OPENAI_API_KEY and MCP_SERVER_PORT to backend/.env file
- [x] T004 [P] Create backend/mcp/ directory structure with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create database migration script backend/migrations/001_add_chat_tables.sql with conversations and messages tables per data-model.md
- [x] T006 Run database migration to create conversations and messages tables
- [x] T007 Create Conversation model in backend/models/conversation.py per data-model.md SQLModel definition
- [x] T008 [P] Create Message model in backend/models/conversation.py with MessageRole enum and validation
- [x] T009 [P] Configure structlog with JSON formatter and correlation ID support in backend/config/logging.py
- [x] T010 [P] Create MCP server initialization in backend/mcp/server.py with Server("todo-mcp-server")
- [x] T011 Create request queue with exponential backoff handler in backend/services/queue_service.py per research.md Section 5
- [x] T012 Create OpenAI agent initialization service in backend/services/agent_service.py with gpt-4o-mini configuration

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Enable users to add tasks by typing natural language like "I need to buy groceries tomorrow"

**Independent Test**: Open chat, type "I need to buy groceries tomorrow", verify task created in database with title "Buy groceries"

### Implementation for User Story 1

- [x] T013 [P] [US1] Implement add_task MCP tool in backend/mcp/tools/add_task.py per contracts/mcp-tools.json schema
- [x] T014 [P] [US1] Register add_task tool with MCP server in backend/mcp/server.py
- [x] T015 [US1] Create ChatRequest and ChatResponse Pydantic models in backend/models/chat.py per contracts/chat-api.yaml
- [x] T016 [US1] Implement chat service with conversation creation logic in backend/services/chat_service.py
- [x] T017 [US1] Implement POST /api/{user_id}/chat endpoint in backend/routes/chat.py with JWT validation per FR-009 to FR-016
- [x] T018 [US1] Add chat router to FastAPI app in backend/main.py
- [x] T019 [US1] Create ChatWindow wrapper component in frontend/src/components/ChatWindow.tsx using OpenAI ChatKit
- [x] T020 [US1] Create chat page in frontend/src/app/chat/page.tsx with auth integration
- [x] T021 [US1] Add /chat navigation link to existing app navigation

**Checkpoint**: User can open chat interface and create tasks via natural language - MVP FUNCTIONAL

---

## Phase 4: User Story 2 - View and Query Tasks (Priority: P1)

**Goal**: Enable users to ask about their tasks and get natural language responses with filtering

**Independent Test**: Add several tasks (some completed, some pending), ask "What do I need to do today?", verify only pending tasks listed

### Implementation for User Story 2

- [ ] T022 [P] [US2] Implement list_tasks MCP tool in backend/mcp/tools/list_tasks.py with status filter per contracts/mcp-tools.json
- [ ] T023 [US2] Register list_tasks tool with MCP server in backend/mcp/server.py
- [ ] T024 [US2] Update agent instructions in backend/services/agent_service.py to recognize list task intent patterns per FR-030
- [ ] T025 [US2] Test list_tasks integration by asking "Show my tasks", "What's pending?", "What have I finished?"

**Checkpoint**: Users can now both create AND view tasks via chat - Core MVP complete

---

## Phase 5: User Story 6 - Resume Conversation Context (Priority: P2)

**Goal**: Users can return after logout/restart and continue conversations with full history preserved

**Independent Test**: Start conversation with 5 messages, restart backend server, open same conversation, verify all 5 messages display

### Implementation for User Story 6

- [ ] T026 [P] [US6] Implement conversation loading logic in backend/services/chat_service.py loading last 50 messages per FR-014
- [ ] T027 [P] [US6] Implement GET /api/{user_id}/conversations endpoint in backend/routes/chat.py for conversation list per contracts/chat-api.yaml
- [ ] T028 [P] [US6] Implement GET /api/{user_id}/conversations/{id}/messages endpoint for message pagination
- [ ] T029 [US6] Add conversation list component in frontend/src/components/ConversationList.tsx showing recent 20 with infinite scroll per FR-058
- [ ] T030 [US6] Add conversation switching logic in frontend/src/app/chat/page.tsx
- [ ] T031 [US6] Implement message pagination UI in ChatWindow component for loading older messages per FR-007
- [ ] T032 [US6] Update conversation.updated_at timestamp trigger per data-model.md migration script

**Checkpoint**: Conversations persist and resume across sessions - Production-ready state management

---

## Phase 6: User Story 3 - Complete Tasks via Chat (Priority: P2)

**Goal**: Users can mark tasks complete by natural language like "Mark groceries task as done"

**Independent Test**: Create task "Buy groceries", say "Mark groceries task as done", verify task.completed = true

### Implementation for User Story 3

- [ ] T033 [P] [US3] Implement complete_task MCP tool in backend/mcp/tools/complete_task.py per contracts/mcp-tools.json
- [ ] T034 [US3] Register complete_task tool with MCP server in backend/mcp/server.py
- [ ] T035 [US3] Update agent instructions to recognize complete intent patterns per FR-031
- [ ] T036 [US3] Handle ambiguous task references by calling list_tasks first when multiple matches possible per acceptance scenario 3

**Checkpoint**: Users can create, view, and complete tasks - Full task lifecycle via chat

---

## Phase 7: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Users can modify task titles/descriptions via natural conversation

**Independent Test**: Create task "Morning Meeting", say "Change task title to Team Standup", verify title updated

### Implementation for User Story 4

- [ ] T037 [P] [US4] Implement update_task MCP tool in backend/mcp/tools/update_task.py with title/description validation per FR-043, FR-044
- [ ] T038 [US4] Register update_task tool with MCP server in backend/mcp/server.py
- [ ] T039 [US4] Update agent instructions to recognize update intent patterns per FR-033
- [ ] T040 [US4] Add clarification handling when user doesn't specify which task to update per acceptance scenario 3

**Checkpoint**: Task modification available via chat

---

## Phase 8: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Users can remove unwanted tasks via natural language

**Independent Test**: Create task "Buy groceries", say "Delete the groceries task", verify task removed from database

### Implementation for User Story 5

- [ ] T041 [P] [US5] Implement delete_task MCP tool in backend/mcp/tools/delete_task.py per contracts/mcp-tools.json
- [ ] T042 [US5] Register delete_task tool with MCP server in backend/mcp/server.py
- [ ] T043 [US5] Update agent instructions to recognize delete intent patterns per FR-032
- [ ] T044 [US5] Handle multiple matching tasks with disambiguation per acceptance scenario 2

**Checkpoint**: All 5 task operations (add, list, complete, update, delete) functional via chat

---

## Phase 9: User Story 7 - Browse and Search Conversations (Priority: P3)

**Goal**: Users can efficiently find and switch between conversations with search capability

**Independent Test**: Create 25 conversations, verify only 20 load initially, scroll to load more, search to find specific conversation

### Implementation for User Story 7

- [ ] T045 [P] [US7] Implement conversation search query in backend/services/chat_service.py with ILIKE search per data-model.md query patterns
- [ ] T046 [P] [US7] Add search parameter to GET /api/{user_id}/conversations endpoint in backend/routes/chat.py
- [ ] T047 [US7] Implement search input component in frontend/src/components/ConversationList.tsx per FR-059
- [ ] T048 [US7] Add date filter UI for conversation search
- [ ] T049 [US7] Implement infinite scroll for conversation list loading per FR-058

**Checkpoint**: Full conversation management UI with search and browse capabilities

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Production-ready quality, observability, and error handling

- [ ] T050 [P] Implement structured logging with correlation IDs across all endpoints per FR-062, FR-063
- [ ] T051 [P] Add sampling logic (1% success, 100% errors) to logger per FR-064
- [ ] T052 [P] Implement metrics tracking for response times, error rates, queue depths per FR-065
- [ ] T053 [P] Add health check endpoint GET /health/mcp for MCP server status per quickstart.md
- [ ] T054 Add input validation for empty/whitespace messages per edge case handling
- [ ] T055 Add character limit validation (1000 chars) with user-friendly error per FR-001
- [ ] T056 [P] Implement conversation retention job (90-day active, 1-year archive) per FR-057 and data-model.md lifecycle
- [ ] T057 [P] Add error boundary component in frontend/src/app/chat/error.tsx for graceful failure handling
- [ ] T058 Implement retry mechanism for transient network failures in frontend chat API calls
- [ ] T059 Add loading states and typing indicators per FR-003
- [ ] T060 [P] Add OpenAI API cost monitoring and alerting dashboard
- [ ] T061 [P] Create deployment documentation with environment variable checklist

**Checkpoint**: Production-ready system with full observability and error handling

---

## Dependencies & Execution Strategy

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation)
                      ↓
        ┌─────────────┴─────────────┬──────────────┬──────────────┐
        ↓                           ↓              ↓              ↓
    US1 (P1) 🎯                 US2 (P1)       US6 (P2)       US3 (P2)
    Create Tasks                View Tasks     Resume         Complete
        ↓                           ↓          Context        Tasks
        └───────────┬───────────────┘              ↓              ↓
                    ↓                              ↓              ↓
                US4 (P3)                       US5 (P3)       US7 (P3)
                Update                         Delete         Browse/Search
                Tasks                          Tasks          Conversations
```

**Parallel Opportunities**:

- **After Foundation (Phase 2)**:
  - US1 and US2 can be implemented in parallel (different MCP tools, independent)
  - US6 can start in parallel with US1/US2 (different endpoints)

- **Within Each User Story**:
  - Tasks marked [P] can run in parallel within that story
  - Example in US1: T013 [P] and T014 [P] can run simultaneously

- **After US1 + US2 Complete**:
  - US3, US4, US5 can be implemented in parallel (different MCP tools)
  - US6 and US7 can be implemented in parallel (different concerns)

### Suggested MVP Scope (Minimum Viable Product)

**MVP Delivery**: User Stories 1 + 2 only
- User Story 1: Create tasks via natural language
- User Story 2: View and query tasks

**Why**: These two stories deliver the core value proposition - natural language task management. Users can add and view tasks conversationally, which demonstrates the chatbot capability.

**Timeline**: Complete Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2)

**Post-MVP Iterations**:
- Iteration 2: Add US6 (conversation persistence)
- Iteration 3: Add US3 (complete tasks)
- Iteration 4: Add US4 + US5 (update + delete)
- Iteration 5: Add US7 (search)

### Implementation Strategy

1. **Sequential Phases**: Phase 1 → Phase 2 must complete before user stories
2. **Parallel User Stories**: After Phase 2, implement US1 and US2 in parallel if team has multiple developers
3. **Independent Testing**: Each user story can be tested independently using its "Independent Test" criteria from spec.md
4. **Incremental Delivery**: Deploy after each user story phase completes for rapid feedback

---

## Parallel Execution Examples

### Example 1: Foundation Phase (Phase 2)

Can run in parallel:
```bash
# Developer 1
Task T007 (Create Conversation model)
Task T008 (Create Message model)

# Developer 2
Task T009 (Configure logging)
Task T010 (Setup MCP server)
```

### Example 2: User Story 1 (Phase 3)

Can run in parallel after T013-T014 complete:
```bash
# Developer 1 (Backend)
Task T015 (ChatRequest/Response models)
Task T016 (Chat service)

# Developer 2 (Frontend)
Task T019 (ChatWindow component)
Task T020 (Chat page)
```

### Example 3: Multiple User Stories

After Phase 2 completes, can parallelize:
```bash
# Team A: US1 (Create tasks)
Tasks T013-T021

# Team B: US2 (View tasks)
Tasks T022-T025

# Team C: US6 (Conversation persistence)
Tasks T026-T032
```

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundation)**: 8 tasks (blocking)
- **Phase 3 (US1 - Create Tasks)**: 9 tasks 🎯 MVP
- **Phase 4 (US2 - View Tasks)**: 4 tasks 🎯 MVP
- **Phase 5 (US6 - Resume Context)**: 7 tasks
- **Phase 6 (US3 - Complete Tasks)**: 4 tasks
- **Phase 7 (US4 - Update Tasks)**: 4 tasks
- **Phase 8 (US5 - Delete Tasks)**: 4 tasks
- **Phase 9 (US7 - Browse/Search)**: 5 tasks
- **Phase 10 (Polish)**: 12 tasks

**Total**: 61 tasks

**Parallelizable**: 23 tasks marked [P] (38%)

**MVP Scope**: Phases 1-4 only (25 tasks) delivers core chatbot capability

---

## Validation Checklist

- [x] All tasks follow format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [x] Task IDs sequential (T001-T061)
- [x] All user story tasks have [Story] labels (US1-US7)
- [x] All tasks include specific file paths
- [x] Setup and Foundation phases have no story labels
- [x] Each user story maps to spec.md user stories
- [x] Independent test criteria defined for each story
- [x] Dependencies documented in execution strategy
- [x] Parallel opportunities identified (23 tasks)
- [x] MVP scope clearly defined (US1 + US2)
- [x] Checkpoints show incremental value delivery

---

## Implementation Notes

### Critical Path

The minimum path to working chatbot:
1. Phase 1 (Setup) - 4 tasks
2. Phase 2 (Foundation) - 8 tasks
3. Phase 3 (US1) - 9 tasks
4. Phase 4 (US2) - 4 tasks

**Total Critical Path**: 25 tasks for MVP

### Risk Mitigation

- **OpenAI API dependency**: Implement queue + retry (T011) early in Foundation phase
- **State management complexity**: Conversation/Message models (T007-T008) in Foundation ensure all stories use same pattern
- **Authorization**: JWT validation in chat endpoint (T017) protects all downstream operations

### Testing Strategy

Integration tests validate each user story independently:
- US1: Create task via chat → verify in database
- US2: Query tasks via chat → verify correct filtering
- US3: Complete task → verify status update
- US4: Update task → verify changes persisted
- US5: Delete task → verify removal
- US6: Resume conversation → verify history loaded
- US7: Search conversations → verify filtering works

Contract tests ensure MCP tool schemas match specification (optional, can add if TDD approach desired).
