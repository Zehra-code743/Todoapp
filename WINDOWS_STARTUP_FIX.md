# Windows Startup Fix - Phase III

## Issue: Frontend Crash on Startup

### Error Code: 3221226505 (0xC0000409)
This Windows error code indicates a stack buffer overrun or memory corruption, typically caused by:
1. Node.js running out of memory during compilation
2. Corrupted Next.js build cache
3. Incorrect environment variable syntax on Windows

## Fixes Applied

### 1. Cross-Platform Environment Variables ✅
**Problem:** The original `NODE_OPTIONS='--max-old-space-size=4096'` syntax doesn't work on Windows PowerShell.

**Solution:** Installed and configured `cross-env` for Windows compatibility.

**Files Modified:**
- `frontend/package.json` - Added `cross-env` to devDependencies
- `frontend/package.json` - Updated build script to use `cross-env`
- `package.json` (root) - Updated `dev:frontend` script

**Changes:**
```json
// frontend/package.json
"scripts": {
  "build": "cross-env NODE_OPTIONS=--max-old-space-size=4096 next build"
},
"devDependencies": {
  "cross-env": "^7.0.3"
}

// package.json (root)
"scripts": {
  "dev:frontend": "cd frontend && cross-env NODE_OPTIONS=--max-old-space-size=4096 npm run dev"
}
```

### 2. Cleaned Next.js Cache ✅
Removed the corrupted `.next` directory that may have contained invalid build artifacts.

### 3. Added Cleanup Scripts ✅
Added convenience scripts to `package.json`:
```json
"clean": "cd frontend && rmdir /s /q .next node_modules && npm install",
"clean:cache": "cd frontend && rmdir /s /q .next"
```

## Startup Instructions

### Option 1: Full Stack (Recommended)
```powershell
npm run dev
```

This starts both backend and frontend together using concurrently.

### Option 2: Separate Terminals

**Terminal 1 - Backend:**
```powershell
cd backend
..\backend\venv\Scripts\python -m uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Option 3: With Explicit Memory Setting
If still having issues:
```powershell
cd frontend
cross-env NODE_OPTIONS=--max-old-space-size=8192 npm run dev
```

## Troubleshooting

### If Frontend Still Crashes

#### 1. Clear All Caches
```powershell
# From root directory
npm run clean:cache

# Or manually
cd frontend
Remove-Item -Recurse -Force .next
```

#### 2. Reinstall Node Modules
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

#### 3. Check Node Version
```powershell
node --version
```
Required: Node.js 18.0.0 or higher

#### 4. Increase Memory Further
Edit `package.json` and increase to 8GB:
```json
"dev:frontend": "cd frontend && cross-env NODE_OPTIONS=--max-old-space-size=8192 npm run dev"
```

#### 5. Check for Port Conflicts
```powershell
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill process if needed (replace PID)
taskkill /PID <PID> /F
```

### If Backend Fails to Start

#### 1. Verify Python Virtual Environment
```powershell
cd backend
..\backend\venv\Scripts\python --version
```

#### 2. Reinstall Backend Dependencies
```powershell
cd backend
..\backend\venv\Scripts\pip install -r requirements.txt
```

#### 3. Check Database Connection
Verify `.env` file has correct `DATABASE_URL`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp_db
```

#### 4. Apply Database Migrations
```powershell
cd backend
..\backend\venv\Scripts\python run_migration.py
```

### Common Issues

#### "Module not found" errors
```powershell
cd frontend
npm install
```

#### "Port already in use"
**Frontend (3000):**
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Backend (8000):**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### Authentication not working
1. Clear browser cookies
2. Restart both servers
3. Sign out and sign in again

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp_db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

# OpenAI API (Phase III)
OPENAI_API_KEY=sk-proj-... (REVOKE THE OLD ONE!)

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Security Reminder

⚠️ **CRITICAL:** Your OpenAI API key was exposed in logs!

**Immediate Actions Required:**
1. Go to https://platform.openai.com/api-keys
2. Find and DELETE the key: `sk-proj-zfpc-...`
3. Generate a new API key
4. Update `backend/.env` with new key
5. Never commit `.env` files to git
6. Verify `.env` is in `.gitignore`

## Verification Steps

### 1. Backend Health Check
```powershell
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. Frontend Access
Open browser: http://localhost:3000
- Should show TodoApp homepage
- Sign in/up should work
- Dashboard should load tasks

### 3. Chat Functionality
1. Navigate to http://localhost:3000/chat
2. Send a test message
3. Verify AI responds

### 4. Database Check
```powershell
cd backend
..\backend\venv\Scripts\python -c "from src.db import engine; print('DB Connected:', engine.url)"
```

## Dependencies Installed

**Root:**
- `concurrently: ^8.2.2` - Run multiple scripts
- `cross-env: ^7.0.3` - Cross-platform env variables

**Frontend:**
- `cross-env: ^7.0.3` - Cross-platform env variables (added)
- All existing Next.js and React dependencies

**Backend:**
- All existing FastAPI and SQLModel dependencies
- No changes required

## Next Steps After Successful Startup

1. **Revoke exposed OpenAI API key** (CRITICAL!)
2. Test authentication flow:
   - Sign up
   - Sign in
   - Access dashboard
   - View tasks
3. Test chat functionality:
   - Navigate to /chat
   - Send messages
   - Verify AI responses
   - Check task operations
4. Review security settings
5. Consider enabling production mode

## Additional Commands

```powershell
# Install all dependencies from scratch
npm run setup

# Run tests
npm run test:frontend
npm run test:backend

# Build for production
cd frontend
npm run build

# Audit security
cd frontend
npm audit
```

## Files Modified in This Fix

1. `frontend/package.json`
   - Added `cross-env` to devDependencies
   - Updated `build` script with cross-env

2. `package.json` (root)
   - Updated `dev:frontend` script with cross-env
   - Added `clean` and `clean:cache` scripts

3. Cleaned `.next` directory (build cache)

---

**Status:** Fixed ✅
**Date:** 2026-01-01
**Phase:** Phase III - Windows Compatibility
**Platform:** Windows 11/10 PowerShell
