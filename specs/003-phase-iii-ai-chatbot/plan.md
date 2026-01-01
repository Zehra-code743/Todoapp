# Implementation Plan: Phase III - Todo AI Chatbot

**Branch**: `003-phase-iii-ai-chatbot` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-phase-iii-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the Todo web application into an AI-powered conversational interface using Model Context Protocol (MCP) architecture. Users will manage tasks through natural language chat powered by OpenAI's gpt-4o-mini model, with MCP tools exposing task operations (add, list, complete, delete, update). The system maintains stateless architecture with all conversation state persisted in PostgreSQL database.

**Key Technical Approach:**
- Backend: Extend existing FastAPI server with chat endpoint and MCP server
- Frontend: Integrate OpenAI ChatKit UI component into Next.js application
- AI Agent: OpenAI Agents SDK with MCP tool registration
- State Management: Database-backed conversations and messages (stateless server)
- Architecture: Event-driven with request queueing and exponential backoff for rate limiting

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 16 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, Official MCP SDK, OpenAI ChatKit, Better Auth (existing)
**Storage**: Neon PostgreSQL (existing database, new tables: conversations, messages)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Cloud-hosted web application (Vercel frontend + backend deployment)
**Project Type**: Web application (fullstack with frontend + backend)
**Performance Goals**: <3s chat response time (95th percentile), 100 concurrent users, <500ms database queries
**Constraints**: <1s MCP tool execution, 99.9% uptime, stateless server (no in-memory state), 90-day conversation retention
**Scale/Scope**: 10,000+ conversations, 50 messages per conversation display, 20 conversations per user list view

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Specification as Single Source of Truth ✅
**Status**: PASS
**Evidence**: Complete spec.md with 65 functional requirements, 20 non-functional requirements, 7 user stories, clarified through /sp.clarify session
**Compliance**: All behavior defined in spec before implementation; code will be generated from spec

### II. AI-Driven Implementation ✅
**Status**: PASS
**Evidence**: Plan created via /sp.plan command; implementation will follow via /sp.implement with Claude Code as implementer
**Compliance**: Human provides spec, AI generates implementation artifacts

### III. Stateless Architecture by Default ✅
**Status**: PASS
**Evidence**:
- FR-014: "System MUST load conversation history from database for each request (stateless operation)"
- NFR-005: "Server MUST maintain zero in-memory state between requests (fully stateless)"
- Architecture explicitly stores all state in PostgreSQL (conversations, messages tables)
**Compliance**: No in-memory session state; database-backed conversation persistence

### IV. Separation of Concerns ✅
**Status**: PASS
**Evidence**:
- Spec defines WHAT (requirements, user stories, acceptance criteria)
- Plan defines HOW (architecture, tech stack, data model)
- CLAUDE.md provides agent implementation guidance
**Compliance**: Clear layer boundaries maintained

### V. Tool-Driven Agent Actions ✅
**Status**: PASS
**Evidence**:
- FR-017 to FR-022: All task operations exposed as MCP tools
- FR-023 to FR-028: Agent uses tools for state mutations
- Agent decides intent → MCP tools execute database operations
**Compliance**: Agent doesn't mutate state directly; uses MCP tool abstraction

### VI. MCP as Control Plane ✅
**Status**: PASS
**Evidence**:
- 5 MCP tools defined: add_task, list_tasks, complete_task, delete_task, update_task
- FR-019: "Each MCP tool MUST validate user_id parameter"
- FR-020: "Each MCP tool MUST return structured JSON response"
- Tools are stateless, auditable, deterministic per constitution
**Compliance**: All AI capabilities exposed via MCP standard

### VII. Transparent Specification Evolution ✅
**Status**: PASS
**Evidence**:
- Spec located at `/specs/003-phase-iii-ai-chatbot/spec.md`
- Git-tracked with version history
- Clarifications section documents refinement (Session 2025-12-31)
**Compliance**: Full traceability of design decisions in version control

---

**Overall Gate Status**: ✅ **PASS** - All 7 constitutional principles satisfied

**No Violations to Justify**: This feature adheres to all architectural governance rules

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── models/
│   ├── conversation.py      # NEW: Conversation and Message models
│   ├── task.py              # Existing from Phase II
│   └── user.py              # Existing from Phase II
├── routes/
│   ├── chat.py              # NEW: Chat API endpoint
│   ├── tasks.py             # Existing from Phase II
│   └── auth.py              # Existing from Phase II
├── services/
│   ├── chat_service.py      # NEW: Chat business logic
│   └── task_service.py      # Existing from Phase II
├── mcp/
│   ├── __init__.py          # NEW: MCP module
│   ├── server.py            # NEW: MCP server initialization
│   └── tools/               # NEW: MCP tool implementations
│       ├── __init__.py
│       ├── add_task.py
│       ├── list_tasks.py
│       ├── complete_task.py
│       ├── delete_task.py
│       └── update_task.py
├── migrations/
│   └── 001_add_chat_tables.sql  # NEW: Database migration
├── tests/
│   ├── mcp/                 # NEW: MCP tool tests
│   ├── routes/              # NEW: Chat endpoint tests
│   └── services/            # NEW: Chat service tests
└── main.py                  # Existing (register chat routes)

frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx     # NEW: Chat page
│   │   └── dashboard/       # Existing from Phase II
│   ├── components/
│   │   ├── ChatWindow.tsx   # NEW: OpenAI ChatKit wrapper
│   │   └── TaskList.tsx     # Existing from Phase II
│   └── hooks/
│       ├── useAuth.ts       # Existing from Phase II
│       └── useChat.ts       # NEW: Chat state management
└── package.json             # Update: Add @openai/chatkit
```

**Structure Decision**: Web application (Option 2) with frontend + backend directories. This matches the existing Phase II structure and adds new chat-specific modules without modifying existing task management code.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitutional principles satisfied.

This table is intentionally empty - no complexity justifications required.
