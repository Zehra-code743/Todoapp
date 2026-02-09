"""
Main FastAPI application for Todo Application Backend
Entry point for the API server
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from src.config import settings
from src.schemas.error_schemas import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    # Import engine here to avoid circular imports
    from src.db import engine

    # Import models to ensure they're registered with SQLModel metadata
    from src.models import User, Task
    from src.models.conversation import Conversation, Message

    # Startup: Create all tables
    SQLModel.metadata.create_all(engine)

    yield

    # Shutdown: Clean up resources
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="Todo Application API",
    description="Phase II Multi-User Todo Application with JWT Authentication",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Todo Application API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from src.api.v1 import health, tasks, auth, chat, citizen
from src.api.v1 import recurring_tasks, reminders, search

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(citizen.router, prefix="/api", tags=["Citizen Reporting"])
app.include_router(recurring_tasks.router, prefix="/api/v1", tags=["Recurring-Tasks"])
app.include_router(reminders.router, prefix="/api/v1", tags=["Reminders"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
