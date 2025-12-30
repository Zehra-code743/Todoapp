# Phase 0: Research & Technical Decisions

**Feature**: Phase II Todo Full-Stack Web Application
**Date**: 2025-12-26
**Status**: Complete

---

## Overview

This document captures research findings and technical decisions for the Phase II multi-user web application. All NEEDS CLARIFICATION items from Technical Context have been resolved through analysis of requirements, best practices, and architectural constraints.

---

## Decision 1: Frontend Framework - Next.js with App Router

**Decision**: Use Next.js 14+ with App Router, React 18+ Server Components, TypeScript

**Rationale**:
- **Server Components by default**: Reduces client-side JavaScript, improves performance
- **Built-in routing**: File-system based, automatic code splitting
- **Vercel deployment**: Zero-config deployment, edge caching, automatic HTTPS
- **TypeScript integration**: First-class support, improved DX
- **Better Auth compatibility**: Works seamlessly with Next.js middleware and API routes

**Alternatives Considered**:
1. **Vite + React SPA**: Simpler but requires manual routing, SSR setup, deployment configuration
2. **Remix**: Modern full-stack framework but less mature ecosystem, steeper learning curve
3. **Create React App**: Deprecated, not recommended for new projects

**Implementation Notes**:
- Use App Router (not Pages Router) for modern patterns
- Server Components for static content, Client Components for interactivity
- Route groups `(auth)` for authentication pages
- `/dashboard` for main application

---

## Decision 2: Backend Framework - FastAPI

**Decision**: FastAPI 0.104+ with async/await, Pydantic v2, SQLModel ORM

**Rationale**:
- **Async by default**: Handles concurrent requests efficiently (target: 100 concurrent users)
- **Automatic API docs**: OpenAPI/Swagger generation, helpful for development
- **Type safety**: Pydantic validation catches errors at API boundary
- **Performance**: Uvicorn ASGI server, comparable to Node.js/Go for I/O-bound tasks
- **Python ecosystem**: Easy integration with future ML/AI features (Phase III)

**Alternatives Considered**:
1. **Django + DRF**: More batteries-included but heavier, slower for simple APIs
2. **Flask**: Lighter but requires more manual setup, lacks async natively
3. **Node.js + Express**: JavaScript full-stack but team familiar with Python

**Implementation Notes**:
- SQLModel for ORM (combines SQLAlchemy + Pydantic)
- Dependency injection for JWT validation
- Middleware for CORS and auth
- Separate `schemas/` for request/response models

---

## Decision 3: Authentication Strategy - Better Auth (Frontend) + JWT Validation (Backend)

**Decision**: Better Auth library on frontend for signup/signin/JWT issuance, backend validates JWT signature

**Rationale**:
- **Better Auth advantages**:
  - Modern, TypeScript-first authentication library
  - Built-in JWT token management with httpOnly cookies
  - Password hashing with bcrypt
  - Session management and refresh tokens
  - Easy integration with Next.js middleware
- **JWT validation backend**:
  - Stateless: No session storage needed
  - Shared secret (`BETTER_AUTH_SECRET`) validates tokens
  - Payload contains `user_id` for authorization
- **Security**: httpOnly cookies prevent XSS attacks, HTTPS prevents interception

**Alternatives Considered**:
1. **NextAuth.js**: More popular but heavier, designed for OAuth providers
2. **Auth0/Clerk**: Third-party SaaS, adds external dependency and cost
3. **Custom JWT implementation**: Reinventing the wheel, security risks

**Implementation Notes**:
- Frontend: Better Auth handles signup, signin, logout, token storage
- Backend: JWT verification middleware extracts `user_id` from token
- Shared secret in environment variables (min 32 characters)
- 7-day token expiration (configurable)

---

## Decision 4: Database - Neon PostgreSQL

**Decision**: Neon Serverless PostgreSQL with connection pooling

**Rationale**:
- **Serverless**: Auto-scaling, pay-per-use, no server management
- **PostgreSQL compatibility**: Standard SQL, ACID guarantees, strong constraints
- **Connection pooling**: Handles serverless function cold starts (important for Vercel deployment)
- **Free tier**: Sufficient for MVP (1GB storage, 10 concurrent connections)
- **Branching**: Database branches for development/staging (nice-to-have)

**Alternatives Considered**:
1. **Supabase**: Full backend-as-a-service, but we only need database
2. **PlanetScale**: MySQL-based, lacks PostgreSQL features (arrays, JSON, full-text search)
3. **Self-hosted PostgreSQL**: Requires infrastructure management

**Implementation Notes**:
- Use SQLModel for ORM (generates SQLAlchemy models + Pydantic validation)
- Indexes: `tasks.user_id`, `tasks.completed`, `users.email` (unique)
- Migrations: Alembic or `create_all()` for Phase II simplicity
- Connection string in `DATABASE_URL` environment variable

---

## Decision 5: State Management - React Query (TanStack Query)

**Decision**: TanStack Query v5 for server state, React hooks for local UI state

**Rationale**:
- **Server state caching**: Reduces API calls, improves perceived performance
- **Optimistic updates**: UI updates before server confirmation (SC-004: <100ms)
- **Automatic refetching**: Keeps data fresh, handles window focus/reconnect
- **Error handling**: Built-in retry logic, error boundaries
- **TypeScript support**: Fully typed hooks

**Alternatives Considered**:
1. **Redux**: Overkill for simple task management, more boilerplate
2. **Zustand**: Good for client state but lacks server state features
3. **SWR**: Similar to React Query but less feature-rich

**Implementation Notes**:
- Query keys: `['tasks', user_id]` for task lists
- Mutations: `createTask`, `updateTask`, `deleteTask`, `toggleComplete`
- Optimistic updates with rollback on error
- Stale time: 1 minute (configurable)

---

## Decision 6: Styling - Tailwind CSS

**Decision**: Tailwind CSS v3+ with utility-first approach

**Rationale**:
- **Rapid development**: No CSS files, styles in JSX
- **Responsive design**: Mobile-first breakpoints (sm:, md:, lg:)
- **Consistency**: Design system via tailwind.config.ts
- **Performance**: PurgeCSS removes unused styles automatically
- **Ecosystem**: shadcn/ui components work with Tailwind (optional)

**Alternatives Considered**:
1. **CSS Modules**: More traditional but verbose, harder to maintain
2. **Styled Components**: Runtime overhead, SSR complexity
3. **Plain CSS**: Maximum flexibility but inconsistent, no utilities

**Implementation Notes**:
- Mobile-first responsive (min-width: 320px)
- Dark mode support via `dark:` variants (nice-to-have)
- Custom colors in config for brand consistency

---

## Decision 7: Testing Strategy

**Decision**:
- **Backend**: pytest with pytest-asyncio for FastAPI endpoints
- **Frontend**: Vitest for unit tests, Playwright for E2E (Phase II nice-to-have)

**Rationale**:
- **Pytest**: Python standard, fixtures for database/auth mocking
- **pytest-asyncio**: Tests async FastAPI endpoints naturally
- **Vitest**: Fast (Vite-powered), compatible with Jest API
- **Playwright**: Modern E2E, works with Next.js, visual testing

**Alternatives Considered**:
1. **unittest**: Python stdlib but more verbose than pytest
2. **Jest**: Frontend standard but slower than Vitest
3. **Cypress**: E2E alternative but less modern than Playwright

**Implementation Notes**:
- Backend: Test each endpoint with valid/invalid auth, edge cases
- Frontend: Test components in isolation (TaskList, TaskForm)
- E2E: Test critical flows (signup → create task → mark complete)
- Coverage goal: 80% for business logic

---

## Decision 8: Deployment Strategy

**Decision**:
- **Frontend**: Vercel (automatic deployment from Git)
- **Backend**: Vercel Serverless Functions (Python runtime)
- **Database**: Neon PostgreSQL (managed)

**Rationale**:
- **Vercel advantages**:
  - Zero-config deployment
  - Automatic HTTPS
  - Edge caching for static assets
  - Preview deployments for PRs
  - Environment variable management
- **Serverless Functions**:
  - Auto-scaling (handles 100+ concurrent users)
  - No server management
  - Pay-per-execution
  - Python 3.11 runtime available

**Alternatives Considered**:
1. **Railway**: Good for containerized apps, but Vercel integrates better with Next.js
2. **Render**: Similar to Railway, good fallback if Vercel Functions insufficient
3. **AWS Lambda + API Gateway**: More complex setup, overkill for MVP

**Implementation Notes**:
- Deploy frontend from `frontend/` directory
- Backend via `vercel.json` config pointing to `backend/src/main.py`
- Environment variables: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `CORS_ORIGINS`
- CD: Auto-deploy main branch, preview branches for PRs

---

## Decision 9: Development Environment

**Decision**:
- **Frontend**: `npm run dev` (Next.js dev server)
- **Backend**: `uvicorn src.main:app --reload` (FastAPI dev server)
- **Database**: Local PostgreSQL via Docker Compose (optional) or Neon dev branch

**Rationale**:
- **Hot reload**: Fast iteration during development
- **Docker Compose**: Consistent local database, matches production PostgreSQL
- **Neon branching**: Create dev branch from main, reset easily

**Implementation Notes**:
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: todoapp
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
```

---

## Decision 10: Error Handling & Observability

**Decision**:
- **Backend**: Structured logging (Python logging module), error responses with HTTP status codes
- **Frontend**: Error boundaries, toast notifications for user feedback
- **Monitoring**: Vercel Analytics (built-in), optional Sentry for error tracking

**Rationale**:
- **Structured logs**: JSON format for searchability
- **HTTP status codes**: Standard REST patterns (400, 401, 403, 404, 422, 500)
- **Error boundaries**: Prevent full app crashes from component errors
- **User feedback**: Toast notifications for success/error states

**Implementation Notes**:
- Backend: Log level INFO for normal, ERROR for exceptions
- Frontend: Display user-friendly messages, log technical details to console
- Vercel Analytics: Page views, Web Vitals (LCP, FID, CLS)

---

## Summary

All technical decisions resolved. No NEEDS CLARIFICATION items remaining.

**Key Technologies**:
- Frontend: Next.js 14+, React 18, TypeScript, Tailwind CSS, React Query, Better Auth
- Backend: FastAPI, SQLModel, Pydantic, python-jose/PyJWT, uvicorn
- Database: Neon PostgreSQL
- Deployment: Vercel (frontend + backend), Neon (database)
- Testing: pytest (backend), Vitest (frontend)

**Next Phase**: Phase 1 - Design data models, API contracts, quickstart guide.
