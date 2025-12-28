# Quick Start Guide: Phase II Todo Application

**Feature**: 002-phase-ii-fullstack-web
**Date**: 2025-12-26
**Target Audience**: Developers implementing or running the application

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Database Setup](#database-setup)
4. [Environment Configuration](#environment-configuration)
5. [Running Locally](#running-locally)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Node.js**: 18.x or 20.x (latest LTS)
- **Python**: 3.11 or 3.12
- **PostgreSQL**: 15+ (for local development, optional with Neon)
- **Git**: Latest version
- **pnpm/npm/yarn**: Package manager for frontend
- **pip**: Python package manager

### Accounts Needed
- **Neon PostgreSQL**: Free account at [neon.tech](https://neon.tech)
- **Vercel**: Free account at [vercel.com](https://vercel.com) (for deployment)
- **GitHub**: For version control and CI/CD

---

## Project Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd todoapp
git checkout 002-phase-ii-fullstack-web
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
# or
pnpm install
# or
yarn install
```

### 3. Install Backend Dependencies

```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Database Setup

### Option 1: Neon PostgreSQL (Recommended for Development)

1. **Create Neon Project**:
   - Sign up at [neon.tech](https://neon.tech)
   - Create new project: "TodoApp"
   - Select region closest to you
   - Copy connection string

2. **Get Connection String**:
   ```
   postgresql://user:password@host.neon.tech/dbname?sslmode=require
   ```

3. **Initialize Database**:
   ```bash
   cd backend
   # Database tables will be created automatically on first run
   # Or run migrations manually:
   alembic upgrade head  # If using Alembic
   ```

### Option 2: Local PostgreSQL with Docker

1. **Start PostgreSQL Container**:
   ```bash
   docker-compose up -d
   ```

2. **Verify Database Running**:
   ```bash
   docker ps  # Should show postgres container
   ```

3. **Connection String**:
   ```
   postgresql://dev:dev@localhost:5432/todoapp
   ```

---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# Authentication
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7

# Server
PORT=8000
ENV=development
```

**Generate BETTER_AUTH_SECRET**:
```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Frontend Environment Variables

Create `frontend/.env.local` file:

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long-here
BETTER_AUTH_URL=http://localhost:3000

# Optional: Analytics
NEXT_PUBLIC_VERCEL_ANALYTICS=false
```

**IMPORTANT**: `BETTER_AUTH_SECRET` must be **identical** in both frontend and backend.

---

## Running Locally

### Terminal 1: Start Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

**Verify Backend**:
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
# or
pnpm dev
# or
yarn dev
```

**Expected Output**:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in 2.3s
```

**Verify Frontend**:
- Open browser: http://localhost:3000
- Should see signup/signin page

---

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_tasks.py

# Run with verbose output
pytest -v
```

**Expected Output**:
```
======================== test session starts ========================
collected 15 items

tests/test_auth.py ......                                      [ 40%]
tests/test_tasks.py .........                                  [100%]

======================== 15 passed in 2.34s ========================
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test
# or
pnpm test

# Run with coverage
npm test -- --coverage

# Run E2E tests (if implemented)
npm run test:e2e
```

### Manual Testing Checklist

1. **Authentication**:
   - [ ] Sign up with valid email/name/password
   - [ ] Sign up with invalid data (should show errors)
   - [ ] Sign up with duplicate email (should fail)
   - [ ] Sign in with correct credentials
   - [ ] Sign in with wrong password (should fail)
   - [ ] Sign out (should redirect to login)

2. **Task Operations**:
   - [ ] Create task with title only
   - [ ] Create task with title + description
   - [ ] Create task with invalid title (empty or >200 chars)
   - [ ] View empty state (no tasks)
   - [ ] View task list (multiple tasks)
   - [ ] Edit task title
   - [ ] Edit task description
   - [ ] Cancel edit (should revert changes)
   - [ ] Mark task complete (checkbox)
   - [ ] Mark task pending (uncheck)
   - [ ] Delete task (should show confirmation)
   - [ ] Cancel deletion (should keep task)

3. **Authorization**:
   - [ ] Create second user account
   - [ ] Verify user A cannot see user B's tasks
   - [ ] Verify user A cannot edit user B's tasks (403 error)

4. **Performance**:
   - [ ] Optimistic UI: Task appears immediately on create
   - [ ] Page loads in <2 seconds
   - [ ] API responses in <500ms

---

## Deployment

### Deploy to Vercel

#### Prerequisites
- Vercel account connected to GitHub
- Neon PostgreSQL database (production instance)

#### Step 1: Configure Neon Production Database

1. Create production branch in Neon (or new project)
2. Copy production connection string
3. Note: Connection pooling enabled by default

#### Step 2: Deploy Frontend

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

**During deployment, set environment variables**:
- `NEXT_PUBLIC_API_URL`: https://api-todoapp.vercel.app (your backend URL)
- `BETTER_AUTH_SECRET`: (same as backend)
- `BETTER_AUTH_URL`: https://todoapp.vercel.app (your frontend URL)

#### Step 3: Deploy Backend

**Option A: Vercel Serverless Functions**

1. Create `vercel.json` in project root:
```json
{
  "builds": [
    {
      "src": "backend/src/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/src/main.py"
    }
  ]
}
```

2. Deploy:
```bash
vercel --prod
```

3. Set environment variables in Vercel dashboard:
   - `DATABASE_URL`: (Neon production connection string)
   - `BETTER_AUTH_SECRET`: (same as frontend)
   - `CORS_ORIGINS`: https://todoapp.vercel.app
   - `JWT_ALGORITHM`: HS256
   - `JWT_EXPIRY_DAYS`: 7

**Option B: Railway/Render (Python Hosting)**

1. Create account on Railway or Render
2. Connect GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables (same as above)

#### Step 4: Update Frontend API URL

Update frontend environment variable:
- `NEXT_PUBLIC_API_URL`: (Your deployed backend URL)

Redeploy frontend:
```bash
vercel --prod
```

#### Step 5: Initialize Production Database

```bash
# Run migrations (if using Alembic)
DATABASE_URL=<production-url> alembic upgrade head

# Or tables will be created automatically on first API call
```

---

## Troubleshooting

### Common Issues

#### 1. Backend won't start: "ModuleNotFoundError"

**Problem**: Python dependencies not installed

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Frontend won't start: "Cannot find module"

**Problem**: Node dependencies not installed

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 3. Database connection error: "could not connect to server"

**Problem**: Database not running or wrong connection string

**Solutions**:
- **Local PostgreSQL**: `docker-compose up -d`
- **Neon**: Verify connection string in `.env`
- **Check firewall**: Allow outbound connections on port 5432

#### 4. Authentication fails: "Invalid JWT signature"

**Problem**: `BETTER_AUTH_SECRET` mismatch between frontend and backend

**Solution**:
- Verify both `.env` files have identical `BETTER_AUTH_SECRET`
- Secret must be at least 32 characters
- Restart both frontend and backend after changing

#### 5. CORS error in browser: "blocked by CORS policy"

**Problem**: Backend CORS not configured for frontend URL

**Solution**:
```bash
# In backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Restart backend.

#### 6. 403 Forbidden when accessing tasks

**Problem**: JWT `user_id` doesn't match URL `user_id`

**Explanation**: This is expected behavior for security. Each user can only access their own tasks.

**Solution**: Ensure frontend sends correct `user_id` from authenticated user's JWT payload.

#### 7. Optimistic updates not working

**Problem**: React Query not configured correctly

**Solution**:
- Verify `QueryClientProvider` wraps app
- Check mutation `onMutate` handlers for optimistic updates
- Inspect browser DevTools Network tab for API calls

### Debug Mode

#### Enable Backend Debug Logging

```python
# backend/src/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Enable Frontend Debug Mode

```bash
# frontend/.env.local
NEXT_PUBLIC_DEBUG=true
```

Then check browser console for detailed logs.

---

## Performance Optimization

### Backend
- **Database**: Ensure indexes exist on `user_id` and `completed` columns
- **Connection Pooling**: Neon handles automatically
- **Caching**: Not needed for Phase II (small data sets)

### Frontend
- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Use `next/image` for any images
- **Bundle Size**: Monitor with `npm run build` (target: <500KB JS)

---

## Monitoring

### Local Development
- **Backend logs**: Terminal output from uvicorn
- **Frontend logs**: Browser DevTools Console
- **Network**: Browser DevTools Network tab

### Production
- **Vercel Analytics**: Built-in (page views, Web Vitals)
- **Vercel Logs**: Dashboard → Functions → Logs
- **Neon Metrics**: Dashboard → Database → Metrics

---

## Next Steps

After successful local setup:

1. **Run tests**: `pytest` (backend), `npm test` (frontend)
2. **Create first user**: Sign up via UI
3. **Create sample tasks**: Add 3-5 tasks to test features
4. **Test all user journeys**: Follow manual testing checklist
5. **Review specification**: Read `spec.md` for full requirements
6. **Review architecture**: Read `plan.md` and `data-model.md`
7. **Deploy to production**: Follow deployment section above

---

## Resources

- **Specification**: `specs/002-phase-ii-fullstack-web/spec.md`
- **Implementation Plan**: `specs/002-phase-ii-fullstack-web/plan.md`
- **Data Model**: `specs/002-phase-ii-fullstack-web/data-model.md`
- **API Contract**: `specs/002-phase-ii-fullstack-web/contracts/openapi.yaml`
- **TypeScript Types**: `specs/002-phase-ii-fullstack-web/contracts/types.ts`

- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Better Auth Docs**: https://better-auth.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Vercel Docs**: https://vercel.com/docs

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review specification and plan documents
3. Consult framework documentation
4. Open GitHub issue with details (error logs, steps to reproduce)

---

**Last Updated**: 2025-12-26
**Version**: 2.0.0
