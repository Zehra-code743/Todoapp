# Development Script - Run Frontend and Backend Concurrently
# Usage: .\dev.ps1

Write-Host "Starting Todo Application..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "backend\venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    cd backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    cd ..
}

# Check if frontend dependencies are installed
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Frontend dependencies not found. Installing..." -ForegroundColor Yellow
    cd frontend
    npm install
    cd ..
}

Write-Host "Starting Backend (FastAPI) on http://localhost:8000" -ForegroundColor Yellow
Write-Host "Starting Frontend (Next.js) on http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Red
Write-Host ""

# Start backend in background
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn src.main:app --reload --port 8000" -PassThru -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend in background
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru -WindowStyle Normal

Write-Host "Backend PID: $($backend.Id)" -ForegroundColor Green
Write-Host "Frontend PID: $($frontend.Id)" -ForegroundColor Green
Write-Host ""
Write-Host "Servers are running in separate windows!" -ForegroundColor Green
Write-Host "Close those windows or press Ctrl+C here to stop." -ForegroundColor Cyan

# Wait for user input to stop
try {
    Wait-Process -Id $backend.Id, $frontend.Id
}
catch {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "`nServers stopped." -ForegroundColor Green
