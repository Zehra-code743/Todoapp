"""
Notification Service for Advanced Todo Application
Handles reminders and notifications
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

from .models import Task, ReminderSettings, Notification
from .notification_service import NotificationService
from .database import get_db_context
from .api_utils import create_success_response, create_error_response
from .event_publisher import event_publisher

# Initialize FastAPI app
app = FastAPI(title="Notification Service", version="1.0.0")

# Global in-memory storage for simulation
notifications_db = []

# Models
class ScheduleReminderRequest(BaseModel):
    task_id: int
    user_id: str
    due_date: str
    reminder_settings: dict  # Will be converted to ReminderSettings

class ScheduleReminderResponse(BaseModel):
    success: bool
    message: str
    notification_id: Optional[int] = None

class CancelReminderRequest(BaseModel):
    task_id: int
    user_id: str

@app.get("/")
async def root():
    return {"message": "Notification Service - Advanced Todo Application"}

@app.post("/api/reminders/schedule", response_model=ScheduleReminderResponse)
async def schedule_reminder(request: ScheduleReminderRequest):
    """
    Schedule a reminder for a task
    """
    try:
        with get_db_context() as db:
            notification_service = NotificationService(db)

            # Process the reminder event to schedule the notification
            notification_service.process_reminder_event(
                task_id=request.task_id,
                user_id=request.user_id,
                due_date=request.due_date,
                reminder_settings_dict=request.reminder_settings
            )

            return ScheduleReminderResponse(
                success=True,
                message=f"Reminder scheduled for task {request.task_id}",
                notification_id=None  # The service handles creation internally
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scheduling reminder: {str(e)}"
        )

@app.post("/api/reminders/cancel", response_model=dict)
async def cancel_reminder(request: CancelReminderRequest):
    """
    Cancel a scheduled reminder for a task
    """
    try:
        with get_db_context() as db:
            notification_service = NotificationService(db)

            success = notification_service.cancel_reminder(
                task_id=request.task_id,
                user_id=request.user_id
            )

            if success:
                return create_success_response(
                    data={"cancelled_task_id": request.task_id},
                    message="Reminder cancelled successfully"
                )
            else:
                return create_error_response(
                    error="Reminder not found or already processed",
                    message="Could not cancel reminder"
                )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling reminder: {str(e)}"
        )

@app.get("/api/users/{user_id}/notifications/pending")
async def get_pending_notifications(user_id: str):
    """
    Get all pending notifications for a user
    """
    try:
        with get_db_context() as db:
            notification_service = NotificationService(db)

            pending_notifications = notification_service.get_pending_notifications(user_id)

            return create_success_response(
                data={"notifications": [notification.dict() for notification in pending_notifications]},
                message=f"Found {len(pending_notifications)} pending notifications"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting pending notifications: {str(e)}"
        )

# Endpoint to handle incoming reminder events from the event stream
@app.post("/api/events/reminder-triggered")
async def handle_reminder_triggered(task_id: int, user_id: str, channel: str):
    """
    Handle reminder triggered events from the event stream
    """
    try:
        # This would typically update notification status or log the event
        return create_success_response(
            data={"task_id": task_id, "user_id": user_id, "channel": channel},
            message="Reminder triggered event received"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error handling reminder triggered event: {str(e)}"
        )

# Endpoint to handle task creation/update events that may have reminder settings
@app.post("/api/events/task-created-or-updated")
async def handle_task_with_reminder(task_id: int, user_id: str, due_date: str, reminder_settings: dict):
    """
    Handle task creation or update events that include reminder settings
    """
    try:
        with get_db_context() as db:
            notification_service = NotificationService(db)

            # Process the reminder event to schedule the notification
            notification_service.process_reminder_event(
                task_id=task_id,
                user_id=user_id,
                due_date=due_date,
                reminder_settings_dict=reminder_settings
            )

            return create_success_response(
                data={"task_id": task_id},
                message="Task with reminder processed successfully"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error handling task with reminder: {str(e)}"
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown"""
    # In a real implementation, we would properly shut down the scheduler
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)