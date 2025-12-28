# Tasks: Phase II Todo Full-Stack Web Application

**Input**: Design documents from `/specs/002-phase-ii-fullstack-web/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, contracts/types.ts

**Tests**: Tests are OPTIONAL for Phase II per specification (manual testing required, automated tests are nice-to-have).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Path Conventions

This is a **Web Application** with separate frontend and backend:
- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Root**: Configuration files (`.env.example`, `docker-compose.yml`, etc.)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [x] T001 Create backend directory structure: backend/src/{models,schemas,api/v1,services,middleware}, backend/tests/
- [x] T002 Create frontend directory structure: frontend/src/{app,components,lib,hooks,types}
- [x] T003 [P] Initialize backend Python project with requirements.txt (FastAPI, SQLModel, Pydantic, python-jose, uvicorn, pytest, pytest-asyncio)
- [x] T004 [P] Initialize frontend Next.js project with package.json (Next.js 14+, React 18, TypeScript, Tailwind CSS, TanStack Query, Better Auth, Zod)
- [x] T005 [P] Create backend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS, JWT_ALGORITHM, JWT_EXPIRY_DAYS
- [x] T006 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL
- [x] T007 [P] Create docker-compose.yml for local PostgreSQL development database
- [x] T008 [P] Configure backend ESLint/Prettier (Python: black, isort, mypy)
- [x] T009 [P] Configure frontend ESLint/Prettier/TypeScript strict mode in tsconfig.json
- [x] T010 [P] Create .gitignore for Python and Node.js projects
- [x] T011 [P] Copy TypeScript interfaces from contracts/types.ts to frontend/src/types/task.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T012 Create backend/src/config.py for environment variable loading (DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS)
- [x] T013 Create backend/src/main.py FastAPI application with CORS middleware configuration
- [x] T014 [P] Create backend/src/models/__init__.py and User model in backend/src/models/user.py per data-model.md
- [x] T015 [P] Create backend/src/models/task.py Task model per data-model.md with user_id foreign key
- [x] T016 Create backend/src/middleware/jwt_auth.py JWT verification middleware using python-jose, extract user_id from token
- [x] T017 Create backend/src/api/deps.py dependency injection for JWT auth (get_current_user function)
- [x] T018 [P] Create backend/src/schemas/task_schemas.py Pydantic models (TaskCreate, TaskUpdate, TaskResponse, TaskListResponse)
- [x] T019 [P] Create backend/src/schemas/error_schemas.py Pydantic error response models
- [x] T020 Create database initialization in backend/src/main.py (SQLModel create_all on startup)
- [x] T021 Create backend/src/api/v1/__init__.py and health check endpoint in backend/src/api/v1/health.py (GET /health)

### Frontend Foundation

- [x] T022 Create frontend/src/lib/auth.ts Better Auth configuration with email/password provider
- [x] T023 Create frontend/src/lib/api-client.ts API client with JWT token injection from Better Auth
- [x] T024 [P] Create frontend/src/app/layout.tsx root layout with TanStack Query QueryClientProvider and Better Auth SessionProvider
- [x] T025 [P] Create frontend/src/app/globals.css with Tailwind CSS imports
- [x] T026 [P] Configure frontend/tailwind.config.ts with mobile-first breakpoints and color scheme
- [x] T027 [P] Create frontend/src/lib/utils.ts utility functions (cn for Tailwind classes, date formatters)
- [x] T028 Create frontend/src/hooks/useAuth.ts custom hook wrapping Better Auth session state
- [x] T029 Create frontend/src/hooks/useTasks.ts React Query hooks (useTasksQuery, useCreateTaskMutation, useUpdateTaskMutation, useDeleteTaskMutation, useToggleTaskMutation)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Account Creation & Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can sign up, log in, and log out with JWT-based authentication

**Independent Test**: Create account via signup form, log out, log back in, verify JWT token stored in httpOnly cookie and redirects work correctly

### Backend Implementation for User Story 1

- [x] T030 [P] [US1] Verify User model from T014 supports Better Auth fields (id, email, name, password_hash, timestamps)
- [x] T031 [US1] Verify JWT middleware from T016 validates Better Auth JWT tokens with shared BETTER_AUTH_SECRET
- [x] T032 [US1] Add authentication error handlers to backend/src/main.py (401 Unauthorized, 403 Forbidden responses)
- [x] T032a [US1] Create backend authentication service (auth_service.py) with password hashing and JWT generation
- [x] T032b [US1] Create backend authentication endpoints (POST /api/auth/signup, /api/auth/signin, /api/auth/signout)

### Frontend Implementation for User Story 1

- [x] T033 [P] [US1] Create frontend/src/app/(auth)/signin/page.tsx sign-in page with email/password form
- [x] T034 [P] [US1] Create frontend/src/app/(auth)/signup/page.tsx sign-up page with email/name/password form, validation (email format, name 2-100 chars, password 8+ chars)
- [x] T035 [US1] Configure Better Auth in frontend/src/lib/auth.ts to handle signup, signin, JWT issuance with 7-day expiry
- [x] T036 [US1] Create frontend/src/app/page.tsx root page that redirects authenticated users to /dashboard, unauthenticated to /signin
- [x] T037 [P] [US1] Create frontend/src/components/ui/ reusable UI primitives (Button, Input, Label, Card) with Tailwind styling
- [x] T038 [US1] Add route protection middleware in frontend/src/middleware.ts using Better Auth to redirect unauthenticated users
- [x] T039 [US1] Implement logout functionality in frontend layout with "Logout" button calling Better Auth signout
- [x] T040 [US1] Add error handling to signin/signup forms (duplicate email, invalid credentials, network errors)

**Checkpoint**: At this point, authentication should be fully functional - users can signup, signin, logout independently

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P2)

**Goal**: Authenticated users can create new tasks and view their personal task list

**Independent Test**: After authentication, create a task with title and optional description, verify it appears in task list sorted by creation date (newest first), verify empty state shows when no tasks exist

### Backend Implementation for User Story 2

- [x] T041 [US2] Verify Task model from T015 includes all fields per data-model.md (id, user_id, title, description, completed, timestamps)
- [x] T042 [US2] Create backend/src/services/task_service.py with get_tasks_by_user(user_id, status_filter) function, query filtering and sorting logic
- [x] T043 [US2] Implement create_task(user_id, title, description) function in task_service.py with validation (title 1-200 chars, description ≤1000)
- [x] T044 [US2] Create backend/src/api/v1/tasks.py with GET /api/{user_id}/tasks endpoint, verify JWT user_id matches path user_id, call get_tasks_by_user, return TaskListResponse
- [x] T045 [US2] Implement POST /api/{user_id}/tasks endpoint in tasks.py, verify JWT user_id, validate request body with TaskCreate schema, call create_task service, return 201 with TaskResponse
- [x] T046 [US2] Add task ownership validation to all endpoints (403 if JWT user_id ≠ path user_id)
- [x] T047 [US2] Add error handling for invalid input (422 validation errors) and database errors (500 internal server error)
- [x] T048 [US2] Register tasks router in backend/src/main.py under /api prefix

### Frontend Implementation for User Story 2

- [x] T049 [US2] Create frontend/src/app/dashboard/page.tsx main dashboard layout with task list section and task creation form
- [x] T050 [P] [US2] Create frontend/src/components/TaskForm.tsx component for adding new tasks (title input, description textarea, submit button)
- [x] T051 [P] [US2] Create frontend/src/components/TaskList.tsx component to display list of tasks with empty state ("No tasks yet" message + CTA)
- [x] T052 [P] [US2] Create frontend/src/components/TaskItem.tsx component to display individual task (title, description, status, timestamps)
- [x] T053 [US2] Implement useTasksQuery hook in frontend/src/hooks/useTasks.ts to fetch tasks via GET /api/{user_id}/tasks with React Query
- [x] T054 [US2] Implement useCreateTaskMutation hook with optimistic update (immediately add task to UI before server confirms)
- [x] T055 [US2] Add form validation to TaskForm using Zod schema (title 1-200 chars required, description ≤1000 optional)
- [x] T056 [US2] Add loading indicators to dashboard (spinner while fetching tasks, disabled submit button during create)
- [x] T057 [US2] Implement error handling with rollback for failed optimistic updates (show error toast, remove task from UI)
- [x] T058 [US2] Add task count display to dashboard (e.g., "5 pending, 2 completed")
- [x] T059 [US2] Style TaskList with Tailwind CSS (responsive grid/list, mobile-friendly, newest first ordering)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (auth + create/view tasks)

---

## Phase 5: User Story 3 - Mark Tasks Complete (Priority: P3)

**Goal**: Users can toggle task completion status with checkbox

**Independent Test**: With existing tasks, click checkbox to toggle pending↔completed, verify immediate UI feedback, strikethrough styling, and persistence to database

### Backend Implementation for User Story 3

- [x] T060 [US3] Create toggle_task_completion(task_id, user_id) function in backend/src/services/task_service.py, toggle completed boolean, update updated_at
- [x] T061 [US3] Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/src/api/v1/tasks.py, verify ownership, call toggle service, return updated task
- [x] T062 [US3] Add 404 error handling if task not found or not owned by user

### Frontend Implementation for User Story 3

- [x] T063 [US3] Add checkbox to TaskItem component (frontend/src/components/TaskItem.tsx) that calls toggle mutation on click
- [x] T064 [US3] Implement useToggleTaskMutation hook in frontend/src/hooks/useTasks.ts with optimistic update (immediately toggle UI state)
- [x] T065 [US3] Add strikethrough styling and muted color to completed tasks in TaskItem.tsx using Tailwind CSS conditional classes
- [x] T066 [US3] Add smooth animation to checkbox toggle (CSS transition on opacity/text-decoration)
- [x] T067 [US3] Handle error cases (403 if trying to toggle another user's task, 404 if task not found)

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently (auth + create/view + toggle complete)

---

## Phase 6: User Story 4 - Edit Task Details (Priority: P4)

**Goal**: Users can update task title and description with inline editing

**Independent Test**: Click "Edit" button on task, modify title/description inline, save changes, verify persistence and success notification

### Backend Implementation for User Story 4

- [x] T068 [US4] Create update_task(task_id, user_id, title, description) function in backend/src/services/task_service.py with validation
- [x] T069 [US4] Implement PUT /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/v1/tasks.py, verify ownership, validate TaskUpdate schema, call update service
- [x] T070 [US4] Return updated task with new updated_at timestamp, handle validation errors (422) and not found (404)

### Frontend Implementation for User Story 4

- [x] T071 [US4] Add edit mode state to TaskItem component (frontend/src/components/TaskItem.tsx) with "Edit" button
- [x] T072 [US4] Replace task display with input fields (title, description) when in edit mode
- [x] T073 [US4] Add "Save" and "Cancel" buttons in edit mode (Enter to save, Escape to cancel)
- [x] T074 [US4] Implement useUpdateTaskMutation hook in frontend/src/hooks/useTasks.ts with optimistic update
- [x] T075 [US4] Add form validation in edit mode (same constraints as create: title 1-200, description ≤1000)
- [x] T076 [US4] Show success notification (toast) when update succeeds (implicit via optimistic UI)
- [x] T077 [US4] Restore original values if user cancels or update fails (rollback optimistic update)
- [x] T078 [US4] Add keyboard shortcuts (Enter to save, Escape to cancel) in edit mode

**Checkpoint**: User Stories 1-4 should all work independently (auth + CRUD operations except delete)

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P5)

**Goal**: Users can permanently delete tasks with confirmation dialog

**Independent Test**: Click "Delete" button, see confirmation dialog, confirm deletion, verify task removed from UI and database

### Backend Implementation for User Story 5

- [x] T079 [US5] Create delete_task(task_id, user_id) function in backend/src/services/task_service.py, verify ownership, delete from database
- [x] T080 [US5] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/src/api/v1/tasks.py, verify ownership, call delete service, return success message
- [x] T081 [US5] Handle errors (403 forbidden if not owner, 404 if task not found)

### Frontend Implementation for User Story 5

- [x] T082 [P] [US5] Create frontend/src/components/DeleteConfirmDialog.tsx confirmation modal component (Tailwind styled)
- [x] T083 [US5] Add "Delete" button to TaskItem component (frontend/src/components/TaskItem.tsx) that opens confirmation dialog
- [x] T084 [US5] Implement useDeleteTaskMutation hook in frontend/src/hooks/useTasks.ts with optimistic removal from UI
- [x] T085 [US5] Show task title in confirmation dialog ("Delete task: [title]?")
- [x] T086 [US5] Show success notification with deleted task title after deletion (implicit via optimistic UI)
- [x] T087 [US5] Handle cancel action (close dialog, no deletion)
- [x] T088 [US5] Restore task to UI if deletion fails (rollback optimistic update with error message)

**Checkpoint**: All 5 user stories should now be independently functional (complete CRUD + auth)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final production readiness

### Performance & Optimization

- [ ] T089 [P] Add database indexes to backend/src/models/ (user_id, completed, created_at) per data-model.md if not auto-created
- [ ] T090 [P] Configure React Query stale time and cache settings in frontend/src/app/layout.tsx (1 minute stale time)
- [ ] T091 [P] Add code splitting to frontend with dynamic imports for heavy components
- [ ] T092 [P] Optimize Tailwind CSS production build (PurgeCSS configuration in tailwind.config.ts)

### Responsive Design & Accessibility

- [ ] T093 [P] Test and fix mobile responsiveness (320px min width) across all pages
- [ ] T094 [P] Add ARIA labels and roles to forms, buttons, and interactive elements for screen readers
- [ ] T095 [P] Ensure keyboard navigation works for all interactions (Tab, Enter, Escape shortcuts)
- [ ] T096 [P] Test with browser zoom (150%, 200%) and verify UI doesn't break

### Error Handling & User Feedback

- [ ] T097 [P] Add toast notification system to frontend (success, error, info messages)
- [ ] T098 [P] Add error boundary component in frontend/src/app/layout.tsx to catch React errors
- [ ] T099 [P] Add network error handling (offline detection, retry logic in API client)
- [ ] T100 [P] Improve error messages to be user-friendly (avoid technical jargon)

### Documentation & Deployment Prep

- [ ] T101 [P] Create backend/README.md with setup instructions (virtualenv, pip install, env vars, database setup)
- [ ] T102 [P] Create frontend/README.md with setup instructions (npm install, env vars, running dev server)
- [ ] T103 [P] Create root README.md following quickstart.md structure (prerequisites, setup, running locally, deployment)
- [ ] T104 [P] Test docker-compose.yml local development setup (PostgreSQL container)
- [ ] T105 Create vercel.json configuration for backend deployment (Python runtime, API routes)
- [ ] T106 Test manual deployment flow per quickstart.md (Vercel frontend, Vercel Functions backend, Neon database)

### Security Hardening

- [ ] T107 [P] Verify CORS configuration in backend only allows frontend domain (not wildcard)
- [ ] T108 [P] Verify JWT secret is at least 32 characters in .env.example
- [ ] T109 [P] Add rate limiting to backend API endpoints (optional, nice-to-have)
- [ ] T110 [P] Verify SQL injection prevention (SQLModel parameterized queries)
- [ ] T111 [P] Verify XSS prevention (React automatic escaping, no dangerouslySetInnerHTML)

### Testing & Validation

- [ ] T112 Run manual testing checklist from quickstart.md (authentication flow, all CRUD operations, authorization checks)
- [ ] T113 Verify performance targets: page load <2s, API <500ms, optimistic updates <100ms
- [ ] T114 Test with multiple users to verify data isolation (user A cannot see/edit user B's tasks)
- [ ] T115 Test all edge cases from spec.md (JWT expiration, network errors, character limits, duplicate emails)
- [ ] T116 Verify all acceptance criteria from spec.md are met (Must Have items)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - **BLOCKS all user stories**
- **User Stories (Phases 3-7)**: All depend on Foundational (Phase 2) completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order: P1 → P2 → P3 → P4 → P5
- **Polish (Phase 8)**: Depends on all user stories (Phases 3-7) being complete

### User Story Dependencies

- **User Story 1 (P1) - Authentication**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2) - Create/View Tasks**: Can start after Foundational - Depends on US1 for authentication, but US1 can be tested independently
- **User Story 3 (P3) - Toggle Complete**: Can start after Foundational - Requires tasks to exist (US2), but can be tested with seeded data
- **User Story 4 (P4) - Edit Tasks**: Can start after Foundational - Requires tasks to exist (US2), but can be tested with seeded data
- **User Story 5 (P5) - Delete Tasks**: Can start after Foundational - Requires tasks to exist (US2), but can be tested with seeded data

**Note**: User Stories 2-5 all depend on authentication (US1), but each is independently testable once US1 is complete.

### Within Each User Story

- Backend tasks before frontend tasks (API must exist before UI can call it)
- Models before services (services depend on models)
- Services before endpoints (endpoints call services)
- Core implementation before edge case handling
- Complete and test story before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003-T011 marked [P] can run in parallel (10 tasks)

**Phase 2 (Foundational)**:
- Backend: T014, T015, T018, T019, T021 marked [P] can run in parallel (5 tasks)
- Frontend: T024, T025, T026, T027 marked [P] can run in parallel (4 tasks)

**Phase 3 (US1)**:
- Backend: T030 [P] can run independently
- Frontend: T033, T034, T037 marked [P] can run in parallel (3 tasks)

**Phase 4 (US2)**:
- Frontend: T050, T051, T052 marked [P] can run in parallel (3 tasks)

**Phase 5 (US3)**: All tasks are sequential (depend on previous completions)

**Phase 6 (US4)**: All tasks are sequential

**Phase 7 (US5)**: T082 [P] can start early, T083-T088 are sequential

**Phase 8 (Polish)**: Most tasks marked [P] can run in parallel (21 out of 28 tasks)

**Cross-Story Parallelism**: Once Phase 2 (Foundational) is complete, different team members can work on different user stories simultaneously:
- Developer A: User Story 1 (T030-T040)
- Developer B: User Story 2 (T041-T059)
- Developer C: User Story 3 (T060-T067)

---

## Parallel Example: Foundational Phase

```bash
# Launch all parallel backend foundational tasks together:
Task T014: "Create User model in backend/src/models/user.py"
Task T015: "Create Task model in backend/src/models/task.py"
Task T018: "Create task Pydantic schemas in backend/src/schemas/task_schemas.py"
Task T019: "Create error Pydantic schemas in backend/src/schemas/error_schemas.py"
Task T021: "Create health check endpoint in backend/src/api/v1/health.py"

# Launch all parallel frontend foundational tasks together:
Task T024: "Create root layout in frontend/src/app/layout.tsx"
Task T025: "Create globals.css in frontend/src/app/globals.css"
Task T026: "Configure Tailwind in frontend/tailwind.config.ts"
Task T027: "Create utility functions in frontend/src/lib/utils.ts"
```

---

## Parallel Example: User Story 2 (Create/View Tasks)

```bash
# Frontend components can be built in parallel (after backend API exists):
Task T050: "Create TaskForm component in frontend/src/components/TaskForm.tsx"
Task T051: "Create TaskList component in frontend/src/components/TaskList.tsx"
Task T052: "Create TaskItem component in frontend/src/components/TaskItem.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T011) → **11 tasks**
2. Complete Phase 2: Foundational (T012-T029) → **18 tasks** (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (T030-T040) → **11 tasks**
4. **STOP and VALIDATE**: Test authentication flow independently (signup, signin, logout, redirects)
5. Deploy/demo if ready → **MVP: 40 tasks total**

### Incremental Delivery (Add User Stories One-by-One)

1. Complete Setup + Foundational (T001-T029) → **29 tasks** → Foundation ready
2. Add User Story 1 (T030-T040) → **11 tasks** → Test independently → Deploy/Demo (MVP with auth only!)
3. Add User Story 2 (T041-T059) → **19 tasks** → Test independently → Deploy/Demo (MVP + create/view tasks)
4. Add User Story 3 (T060-T067) → **8 tasks** → Test independently → Deploy/Demo (MVP + task completion)
5. Add User Story 4 (T068-T078) → **11 tasks** → Test independently → Deploy/Demo (MVP + task editing)
6. Add User Story 5 (T079-T088) → **10 tasks** → Test independently → Deploy/Demo (Full CRUD complete)
7. Add Polish (T089-T116) → **28 tasks** → Final production-ready application

**Total: 116 tasks**

### Parallel Team Strategy

With multiple developers (after Foundational phase complete):

1. **Week 1**: Team completes Setup + Foundational together (T001-T029) → **29 tasks**
2. **Week 2-3**: Parallel user story development:
   - Developer A: User Story 1 - Authentication (T030-T040) → **11 tasks**
   - Developer B: User Story 2 - Create/View Tasks (T041-T059) → **19 tasks**
   - Developer C: User Story 3 - Toggle Complete (T060-T067) → **8 tasks**
3. **Week 4**: Remaining stories and integration:
   - Developer A: User Story 4 - Edit Tasks (T068-T078) → **11 tasks**
   - Developer B: User Story 5 - Delete Tasks (T079-T088) → **10 tasks**
   - Developer C: Polish tasks (T089-T100) → **12 tasks**
4. **Week 5**: Final polish, testing, deployment (T101-T116) → **16 tasks**

---

## Task Count Summary

| Phase | Description | Task Count | Parallel Opportunities |
|-------|-------------|------------|------------------------|
| Phase 1 | Setup | 11 tasks | 9 tasks [P] |
| Phase 2 | Foundational | 18 tasks | 9 tasks [P] |
| Phase 3 | User Story 1 (P1) | 11 tasks | 3 tasks [P] |
| Phase 4 | User Story 2 (P2) | 19 tasks | 3 tasks [P] |
| Phase 5 | User Story 3 (P3) | 8 tasks | 0 tasks [P] |
| Phase 6 | User Story 4 (P4) | 11 tasks | 0 tasks [P] |
| Phase 7 | User Story 5 (P5) | 10 tasks | 1 task [P] |
| Phase 8 | Polish | 28 tasks | 21 tasks [P] |
| **TOTAL** | **All Phases** | **116 tasks** | **46 tasks [P] (40%)** |

**MVP Scope** (User Story 1 only): **40 tasks** (Phases 1-3)
**Production-Ready** (All User Stories + Polish): **116 tasks**

---

## Notes

- **[P] tasks** (46 total) = different files, no dependencies - can run in parallel
- **[Story] labels** (US1-US5) map tasks to specific user stories for traceability
- Each user story should be independently completable and testable after Foundational phase
- **No automated tests included** per Phase II spec (manual testing required, automated tests are nice-to-have)
- Commit after each task or logical group for incremental progress
- Stop at any checkpoint to validate story independently
- **Performance targets**: <500ms API p95, <2s page load, <100ms optimistic updates
- **Security**: JWT validation on every request, user data isolation, httpOnly cookies
- **Deployment**: Frontend (Vercel), Backend (Vercel Functions or Railway), Database (Neon PostgreSQL)
