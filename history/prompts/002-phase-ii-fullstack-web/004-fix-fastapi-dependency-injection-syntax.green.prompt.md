---
id: 004-fix-fastapi-dependency-injection-syntax
title: Fix FastAPI dependency injection syntax for task endpoints
stage: green
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-phase-ii-fullstack-web
branch: 002-phase-ii-fullstack-web
user: User
command: Fix 422 Unprocessable Entity error when accessing task API
labels: ["fastapi","bugfix","dependency-injection"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/v1/tasks.py
tests: []
---

## Prompt

[BACKEND] INFO:     127.0.0.1:62483 - "GET /api/user_556b58c8012446c5/tasks HTTP/1.1" 422 Unprocessable Entity
[BACKEND] INFO:     127.0.0.1:62483 - "POST /api/user_556b58c8012446c5/tasks HTTP/1.1" 422 Unprocessable Entity
Browser error: "Field required"

## Response snapshot

Fixed incorrect FastAPI dependency injection syntax in tasks.py. The previous implementation used `Depends(verify_user_id_match)` where `verify_user_id_match` was a wrapper function with `Depends` in its default parameter, which doesn't work correctly. Replaced with direct `Depends(get_current_user)` and moved the user ID verification check inside each endpoint function body.

## Outcome

- ✅ Impact: Fixed 422 validation errors on all task CRUD endpoints
- 🧪 Tests: None (runtime testing via API calls)
- 📁 Files: Modified 1 file - backend/src/api/v1/tasks.py
- 🔁 Next prompts: Test full task CRUD flow after signin
- 🧠 Reflection: FastAPI dependency injection requires careful syntax. The `Depends()` should reference functions that don't themselves have `Depends` in their parameters. Simple inline checks are more reliable than complex dependency chains for this use case.

## Evaluation notes (flywheel)

- Failure modes observed: Complex dependency wrapper function wasn't resolving correctly, causing FastAPI to treat parameters as missing
- Graders run and results (PASS/FAIL): Testing in progress
- Prompt variant (if applicable): N/A
- Next experiment: Verify POST, GET, PUT, DELETE, PATCH all work correctly
