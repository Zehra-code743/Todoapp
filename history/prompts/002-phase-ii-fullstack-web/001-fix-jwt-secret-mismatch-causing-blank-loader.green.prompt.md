---
id: PHR-001
title: Fix JWT secret mismatch causing blank loader
stage: green
feature: 002-phase-ii-fullstack-web
date_iso: 2025-12-29
model: claude-sonnet-4-5-20250929
surface: agent
user: User
branch: 002-phase-ii-fullstack-web
command: npm run dev
labels:
  - "bug-fix"
  - "jwt"
  - "authentication"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/.env.local
  - backend/.env
tests: []
prompt_text: |
  mai jab npm run dev chalarahi ho tu mere local host per khali loader dikh raha hai.

response_text: |
  Fixed JWT secret mismatch between frontend and backend. The BETTER_AUTH_SECRET in both .env files was set to a placeholder value, causing JWT token verification to fail with 422 Unprocessable Entity errors. Updated both files to use a matching 32-character secret key: `todoapp-phase2-jwt-secret-key-2025-very-secure-32ch`
outcome:
  status: resolved
  verification: Dashboard now loads with 200 status, API calls succeed
---
