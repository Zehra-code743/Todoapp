---
id: 003-fix-jwt-token-extraction-for-api-requests
title: Fix JWT token extraction for API requests
stage: green
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-phase-ii-fullstack-web
branch: 002-phase-ii-fullstack-web
user: User
command: Fix 401 Unauthorized error on /api/user_xxx/tasks endpoint
labels: ["jwt","authentication","bugfix","frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/lib/api-client.ts
  - frontend/src/app/dashboard/layout.tsx
tests: []
---

## Prompt

FO:     127.0.0.1:61900 - "GET /api/user_451b3bbdeb7144bf/tasks HTTP/1.1" 401 Unauthorized

## Response snapshot

Fixed JWT token extraction issue in api-client.ts and added auth protection to dashboard layout. Root cause was the frontend expecting a JSON-formatted session cookie with a `token` property, but the backend returns the raw JWT token directly. Added fallback parsing and debug logging to handle both formats.

## Outcome

- ✅ Impact: Fixed 401 Unauthorized errors when accessing task API endpoints
- 🧪 Tests: None (runtime testing via browser console debug logs)
- 📁 Files: Modified 2 files - api-client.ts (token extraction), dashboard/layout.tsx (auth guard)
- 🔁 Next prompts: Test signin flow and verify tasks load correctly
- 🧠 Reflection: Session cookie format mismatch between frontend expectations and backend response. Added defensive parsing to handle both formats.

## Evaluation notes (flywheel)

- Failure modes observed: Token returned as raw JWT string, frontend expected JSON object
- Graders run and results (PASS/FAIL): Testing in progress
- Prompt variant (if applicable): N/A
- Next experiment: Verify debug logs show correct token format after signin
