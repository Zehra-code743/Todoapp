---
id: 002
title: Create Implementation Plan
stage: plan
date: 2025-12-26
surface: agent
model: claude-sonnet-4-5
feature: 002-phase-ii-fullstack-web
branch: 002-phase-ii-fullstack-web
user: pc
command: /sp.plan
labels: ["planning", "architecture", "phase-ii", "web-application", "technical-design"]
links:
  spec: specs/002-phase-ii-fullstack-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-phase-ii-fullstack-web/plan.md
  - specs/002-phase-ii-fullstack-web/research.md
  - specs/002-phase-ii-fullstack-web/data-model.md
  - specs/002-phase-ii-fullstack-web/contracts/openapi.yaml
  - specs/002-phase-ii-fullstack-web/contracts/types.ts
  - specs/002-phase-ii-fullstack-web/quickstart.md
  - CLAUDE.md (updated with TypeScript/Next.js context)
tests:
  - N/A (planning stage)
---

## Prompt

User invoked `/sp.plan` command to create implementation plan for Phase II full-stack web application based on the previously completed specification (specs/002-phase-ii-fullstack-web/spec.md).

**Context**: Phase II transforms the console application from Phase I into a multi-user web application with:
- JWT-based authentication (Better Auth)
- RESTful API backend (FastAPI/Python)
- React frontend (Next.js 14+, TypeScript)
- PostgreSQL database (Neon)
- Vercel deployment

## Response snapshot

**Actions Taken**:

1. **Setup and Context Loading**:
   - Ran `setup-plan.ps1` to initialize plan template
   - Loaded constitution.md (version 1.0.0) and feature spec
   - Loaded plan template structure

2. **Technical Context (plan.md)**:
   - **Frontend**: TypeScript 5.x, Next.js 14+ (App Router), React 18+, Better Auth, TanStack Query, Tailwind CSS, Zod
   - **Backend**: Python 3.11+, FastAPI 0.104+, SQLModel/SQLAlchemy, Pydantic v2, python-jose/PyJWT, uvicorn
   - **Database**: Neon PostgreSQL with connection pooling, indexes on user_id/completed/email
   - **Deployment**: Vercel (frontend + backend), Neon (database)
   - **Testing**: pytest (backend), Vitest (frontend), Playwright (E2E nice-to-have)
   - **Performance Goals**: <500ms API p95, <2s page load, <100ms optimistic updates, 100 concurrent users
   - **Constraints**: <200ms p95 latency, 320px min width, keyboard navigation

3. **Constitution Check**: ✅ **ALL 7 PRINCIPLES PASS**
   - Specification as Single Source of Truth: PASS (comprehensive spec.md exists)
   - AI-Driven Implementation: PASS (100% code generation planned)
   - Stateless Architecture: PASS (React components stateless, FastAPI stateless handlers, PostgreSQL for state)
   - Separation of Concerns: PASS (spec defines WHAT, CLAUDE.md defines HOW, agents execute, infrastructure deploys)
   - Tool-Driven Agent Actions: PASS (Write, Edit, Bash tools only)
   - MCP as Control Plane: PASS (Claude Code operates via MCP)
   - Transparent Specification Evolution: PASS (specs in /specs, Git version control)

4. **Project Structure**:
   - **Web Application (Option 2)**: Separate frontend/ and backend/ monorepo
   - Frontend: Next.js App Router structure with `app/`, `components/`, `lib/`, `hooks/`, `types/`
   - Backend: FastAPI structure with `src/main.py`, `models/`, `schemas/`, `api/v1/`, `services/`, `middleware/`
   - Clear separation enables independent deployment (Vercel frontend, Vercel Functions/Railway backend)

5. **Phase 0: Research (research.md)** - 10 Technical Decisions Documented:
   - **Decision 1**: Next.js 14+ with App Router (server components, built-in routing, Vercel integration)
   - **Decision 2**: FastAPI (async, auto API docs, Pydantic validation, Python ecosystem)
   - **Decision 3**: Better Auth + JWT validation (modern TypeScript-first, httpOnly cookies, stateless backend)
   - **Decision 4**: Neon PostgreSQL (serverless, connection pooling, free tier, PostgreSQL compatibility)
   - **Decision 5**: TanStack Query v5 (server state caching, optimistic updates, error handling)
   - **Decision 6**: Tailwind CSS (rapid development, responsive, performance)
   - **Decision 7**: pytest + Vitest (backend + frontend testing)
   - **Decision 8**: Vercel deployment (zero-config, automatic HTTPS, serverless functions)
   - **Decision 9**: Docker Compose for local dev (optional PostgreSQL container)
   - **Decision 10**: Structured logging + error boundaries (observability)

   Each decision includes: Decision, Rationale, Alternatives Considered, Implementation Notes

6. **Phase 1: Data Model (data-model.md)**:
   - **User Entity**: id (TEXT UUID), email (UNIQUE), name, password_hash, timestamps
   - **Task Entity**: id (INTEGER), user_id (FK), title (1-200), description (≤1000), completed (BOOLEAN), timestamps
   - **Relationship**: One-to-Many (User → Task), CASCADE delete
   - **Indexes**: users.email (unique), tasks.user_id, tasks.completed, tasks.created_at
   - **Validation Rules**: Title 1-200 chars, description ≤1000, email unique, password ≥8 chars
   - **State Transitions**: Created → Pending ↔ Completed → Deleted
   - **Query Patterns**: 7 documented patterns with expected performance (<50ms)
   - **Security**: User-level isolation, ownership checks in WHERE clause, no cross-user access
   - **SQLModel + TypeScript interfaces** provided

7. **Phase 1: API Contracts (contracts/)**:
   - **OpenAPI 3.1 Specification** (contracts/openapi.yaml):
     - Health check endpoint (GET /health) - no auth
     - 6 task endpoints (GET/POST/PUT/DELETE/PATCH) - JWT auth required
     - Authorization: Bearer JWT token, user_id validation
     - Schemas: Task, TaskCreate, TaskUpdate, Error, ValidationError
     - Responses: 200/201/400/401/403/404/422/500

   - **TypeScript Interfaces** (contracts/types.ts):
     - Data models: User, Task, OptimisticTask
     - Request/Response types: TaskCreateRequest, TaskUpdateRequest, TaskListResponse
     - Error types: ApiError, ValidationError
     - Query parameters: TaskStatus, TaskListQueryParams
     - React Query key factories: `taskKeys` for consistent cache keys
     - Type guards: isApiError, isValidationError
     - Utility functions: formatApiError, getFirstValidationError
     - Validation constants: TASK_TITLE_MIN_LENGTH, TASK_TITLE_MAX_LENGTH, etc.

8. **Phase 1: Quickstart Guide (quickstart.md)**:
   - **Prerequisites**: Node.js 18+, Python 3.11+, PostgreSQL 15+ (or Neon), accounts (Neon, Vercel, GitHub)
   - **Project Setup**: Clone, install dependencies (npm + pip)
   - **Database Setup**: Neon PostgreSQL (recommended) OR local Docker Compose
   - **Environment Configuration**: Backend `.env` and frontend `.env.local` with identical `BETTER_AUTH_SECRET`
   - **Running Locally**: Two terminals (backend uvicorn, frontend npm run dev)
   - **Testing**: Backend pytest, frontend Vitest, manual testing checklist (authentication, CRUD, authorization, performance)
   - **Deployment**: Vercel (frontend + backend serverless) OR Railway/Render (backend container)
   - **Troubleshooting**: 7 common issues with solutions (module errors, database connection, JWT mismatch, CORS, 403 errors, optimistic updates, debug mode)
   - **Monitoring**: Local (logs, browser DevTools) and production (Vercel Analytics, logs)

9. **Agent Context Update**:
   - Ran `update-agent-context.ps1 -AgentType claude`
   - Updated CLAUDE.md with TypeScript 5.x + Next.js 14+ context
   - Preserved existing manual additions between markers

**Key Architectural Decisions**:

1. **Monorepo Structure**: frontend/ + backend/ in single repo (clean separation, shared tooling)
2. **Authentication Flow**: Better Auth (frontend) issues JWT → Backend validates signature → Shared secret synchronization
3. **Stateless Design**: No server-side sessions, JWT in httpOnly cookies, all state in PostgreSQL
4. **User Isolation**: All task queries filter by `user_id` from JWT payload, ownership checks prevent cross-user access
5. **Optimistic UI**: React Query mutations with `onMutate` for immediate feedback, rollback on error
6. **API Design**: RESTful endpoints `/api/{user_id}/tasks`, user_id validation against JWT
7. **Performance Strategy**: Database indexes, connection pooling, optimistic updates, code splitting, <500ms API target
8. **Security Measures**: httpOnly cookies, JWT signature validation, SQL injection prevention (parameterized queries), CORS whitelist, password hashing (bcrypt)

## Outcome

- ✅ Impact: Complete implementation plan with Phase 0 research, Phase 1 design (data model, contracts, quickstart), and agent context update; ready for `/sp.tasks` command
- 🧪 Tests: Planning stage - no tests; implementation phase will include pytest (backend) and Vitest (frontend) tests
- 📁 Files: 7 files created/updated (plan.md, research.md, data-model.md, openapi.yaml, types.ts, quickstart.md, CLAUDE.md)
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown for implementation
- 🧠 Reflection: Comprehensive planning achieved with clear technical decisions, constitutional compliance, and actionable artifacts; specification-to-implementation workflow fully realized

## Evaluation notes (flywheel)

- Failure modes observed: None - all steps executed successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASS (7/7 principles), Project Structure validation - PASS
- Prompt variant (if applicable): Standard /sp.plan workflow following template
- Next experiment (smallest change to try): Consider generating example Pydantic schemas and React Query hook stubs in contracts/ for faster implementation kickstart
