@echo off
cd backend
venv\Scripts\python -m uvicorn src.main:app --reload --port 8000
