"""
Recurring Task Service for Advanced Todo Application
Handles recurring task creation based on completion events
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

from .models import Task
from .recurring_service import RecurringTaskService
from .database import get_db_context
from .api_utils import create_success_response, create_error_response
from .event_publisher import event_publisher

# Initialize FastAPI app
app = FastAPI(title="Recurring Task Service", version="1.0.0")

# Models
class RecurringTaskProcessRequest(BaseModel):
    task_id: int
    user_id: str

class RecurringTaskProcessResponse(BaseModel):
    success: bool
    message: str
    new_task_id: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "Recurring Task Service - Advanced Todo Application"}

@app.post("/api/process-completion", response_model=RecurringTaskProcessResponse)
async def process_task_completion(request: RecurringTaskProcessRequest):
    """
    Process a task completion event and create a new recurring instance if needed
    """
    try:
        with get_db_context() as db:
            recurring_service = RecurringTaskService(db)

            # Process the task completion event
            recurring_service.process_task_completion_event(
                task_id=request.task_id,
                user_id=request.user_id
            )

            return RecurringTaskProcessResponse(
                success=True,
                message=f"Processed completion for task {request.task_id}",
                new_task_id=None  # The service handles creation internally
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing task completion: {str(e)}"
        )

@app.get("/api/users/{user_id}/upcoming-recurrences")
async def get_upcoming_recurrences(user_id: str, days_ahead: int = 7):
    """
    Get upcoming recurring tasks that will be created in the next N days
    """
    try:
        with get_db_context() as db:
            recurring_service = RecurringTaskService(db)

            upcoming_tasks = recurring_service.get_upcoming_recurring_tasks(
                user_id=user_id,
                days_ahead=days_ahead
            )

            return create_success_response(
                data={"upcoming_tasks": [task.dict() for task in upcoming_tasks]},
                message=f"Found {len(upcoming_tasks)} upcoming recurring tasks"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting upcoming recurrences: {str(e)}"
        )

# Simulate event consumption from Kafka
# In a real implementation, this would be a Kafka consumer
@app.post("/api/events/task-completed")
async def handle_task_completed_event(task_id: int, user_id: str):
    """
    Handle task completed events from the event stream
    """
    try:
        with get_db_context() as db:
            recurring_service = RecurringTaskService(db)

            recurring_service.process_task_completion_event(task_id, user_id)

            return create_success_response(
                data={"processed_task_id": task_id},
                message="Task completion event processed successfully"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error handling task completed event: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)