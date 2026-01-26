"""
Task Service for Advanced Todo Application
Implements CRUD operations for tasks with advanced features
"""
import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from dapr.ext.fastapi import DaprApp
from contextlib import contextmanager

# Import our custom modules
from .models import Task, TaskUpdate, TaskBase, RecurrenceSettings, ReminderSettings
from .task_service import TaskService
from .database import get_db_context
from .api_utils import create_success_response, create_error_response, handle_not_found
from .event_publisher import event_publisher

# Initialize FastAPI app
app = FastAPI(title="Task Service", version="1.0.0")
dapr_app = DaprApp(app)

@app.get("/")
async def root():
    return {"message": "Task Service - Advanced Todo Application"}

@app.post("/api/{user_id}/tasks", response_model=Task, status_code=201)
async def create_task_endpoint(user_id: str, task: TaskBase):
    """
    Create a new task with advanced features
    """
    try:
        with get_db_context() as db:
            task_service = TaskService(db)

            created_task = task_service.create_task(
                user_id=user_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                tags=task.tags,
                due_date=task.due_date,
                is_recurring=task.is_recurring,
                recurrence_settings=task.recurrence_settings,
                reminder_settings=task.reminder_settings
            )

            return created_task

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@app.get("/api/{user_id}/tasks", response_model=List[Task])
async def list_tasks_endpoint(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by task priority"),
    tag: Optional[str] = Query(None, description="Filter by task tag"),
    created_after: Optional[str] = Query(None, description="Filter tasks created after this date"),
    created_before: Optional[str] = Query(None, description="Filter tasks created before this date"),
    sort_by: Optional[str] = Query('created_at', description="Field to sort by"),
    sort_order: Optional[str] = Query('desc', description="Sort order"),
    q: Optional[str] = Query(None, description="Search query for full-text search")
):
    """
    List tasks with filtering, sorting, and search capabilities
    """
    try:
        with get_db_context() as db:
            task_service = TaskService(db)

            # Convert string enums to proper enum objects
            from .models import TaskStatusEnum, PriorityEnum
            status_enum = TaskStatusEnum(status) if status else None
            priority_enum = PriorityEnum(priority) if priority else None

            tasks = task_service.get_tasks(
                user_id=user_id,
                status=status_enum,
                priority=priority_enum,
                tag=tag,
                created_after=created_after,
                created_before=created_before,
                sort_by=sort_by,
                sort_order=sort_order,
                search_query=q
            )

            return tasks

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task_endpoint(task_id: int):
    """
    Get a specific task
    """
    try:
        with get_db_context() as db:
            task_service = TaskService(db)
            task = task_service.get_task(task_id)

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            return task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task_endpoint(task_id: int, task_update: TaskUpdate):
    """
    Update a task
    """
    try:
        with get_db_context() as db:
            task_service = TaskService(db)
            updated_task = task_service.update_task(task_id, task_update)

            if not updated_task:
                raise HTTPException(status_code=404, detail="Task not found")

            return updated_task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_task_endpoint(task_id: int):
    """
    Delete a task
    """
    try:
        with get_db_context() as db:
            task_service = TaskService(db)
            success = task_service.delete_task(task_id)

            if not success:
                raise HTTPException(status_code=404, detail="Task not found")

            return

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

@app.put("/api/tasks/{task_id}/complete", response_model=Task)
async def complete_task_endpoint(task_id: int):
    """
    Mark a task as completed
    """
    try:
        with get_db_context() as db:
            task_service = TaskService(db)
            completed_task = task_service.complete_task(task_id)

            if not completed_task:
                raise HTTPException(status_code=404, detail="Task not found")

            return completed_task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing task: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)