@echo off
echo ========================================
echo Starting Todo Application...
echo ========================================
echo.
echo Checking prerequisites...

REM Check if backend .env exists
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found! Creating from template...
    copy backend\.env.example backend\.env >nul 2>&1
    echo [INFO] Please update backend\.env with your database credentials
)

REM Check if frontend .env.local exists
if not exist "frontend\.env.local" (
    echo [WARNING] frontend\.env.local not found! Creating from template...
    copy frontend\.env.local.example frontend\.env.local >nul 2>&1
    echo [INFO] Please update frontend\.env.local with your API URL
)

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo [INFO] Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Starting servers in separate windows...
echo Press Ctrl+C in each window to stop.
echo.

REM Start backend in new window
start "Backend (FastAPI)" cmd /k "cd /d %CD%\backend && venv\Scripts\python -m uvicorn src.main:app --reload --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
start "Frontend (Next.js)" cmd /k "cd /d %CD%\frontend && npm run dev"

echo.
echo [SUCCESS] Both servers started in separate windows!
echo Close those windows to stop the servers.
echo.
