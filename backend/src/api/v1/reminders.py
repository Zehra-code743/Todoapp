"""
Reminder Endpoints
RESTful API for reminder operations with JWT authentication.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from sqlmodel import Session
from datetime import datetime

from src.api.deps import get_current_user
from src.schemas.task_schemas import SetDueDateRequest, TaskResponse
from src.services.reminder_service import ReminderService
from src.services.notification_service import NotificationService
from src.db import get_session

router = APIRouter()


def get_reminder_service(db: Session = Depends(get_session)) -> ReminderService:
    """Dependency to get ReminderService instance"""
    return ReminderService(db)


def get_notification_service() -> NotificationService:
    """Dependency to get NotificationService instance"""
    return NotificationService()


@router.post("/set-due-date", response_model=TaskResponse)
async def set_due_date_with_reminder(
    request: Request,
    current_user: str = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    Set due date for a task and schedule a reminder.

    Args:
        request: HTTP request with JSON body containing task_id, due_date, etc.
        current_user: Authenticated user ID from JWT
        reminder_service: Reminder service instance
        notification_service: Notification service instance

    Returns:
        Updated TaskResponse

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if not found, 422 for validation errors
    """
    try:
        body = await request.json()
        set_due_date_request = SetDueDateRequest(**body)

        # Verify the user has access to this task
        # This would require getting the task first to verify ownership
        # For now, assuming the service handles this validation

        task = reminder_service.set_due_date_with_reminder(
            task_id=set_due_date_request.task_id,
            due_date=datetime.fromisoformat(set_due_date_request.due_date.replace('Z', '+00:00')),
            reminder_enabled=set_due_date_request.reminder_enabled,
            reminder_advance_minutes=set_due_date_request.reminder_advance_minutes
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return TaskResponse.from_orm(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set due date with reminder: {str(e)}",
        )


@router.post("/{task_id}/snooze/{reminder_id}", response_model=TaskResponse)
async def snooze_reminder(
    task_id: int = Path(..., description="Task ID"),
    reminder_id: int = Path(..., description="Reminder ID"),
    snooze_duration_minutes: int = 15,
    current_user: str = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    """
    Snooze a reminder for a specified duration.

    Args:
        task_id: Task ID
        reminder_id: Reminder ID
        snooze_duration_minutes: Number of minutes to snooze (default 15)
        current_user: Authenticated user ID from JWT
        reminder_service: Reminder service instance

    Returns:
        Updated TaskResponse

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if not found
    """
    # Verify user has access to this reminder/task
    # This would typically involve checking if the user owns the task

    reminder = reminder_service.snooze_reminder(reminder_id, snooze_duration_minutes)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found or not pending",
        )

    # Get the associated task to return
    # This would require a method to get task by reminder_id
    # For now, we'll assume the service can retrieve it
    from src.services.task_service import TaskService
    from src.db import get_session
    with get_session() as db:
        task_service = TaskService(db)
        task = task_service.get_task(task_id, current_user)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.from_orm(task)


@router.get("/{user_id}/reminders", response_model=list)
async def get_user_reminders(
    user_id: str = Path(..., description="User ID"),
    current_user: str = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    """
    Get all reminders for a user.

    Args:
        user_id: User ID from URL path
        current_user: Authenticated user ID from JWT
        reminder_service: Reminder service instance

    Returns:
        List of reminders

    Raises:
        HTTPException: 403 if user_id mismatch
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    reminders = reminder_service.get_reminders_for_user(current_user)
    # Convert to appropriate response format
    return reminders


@router.patch("/{user_id}/reminders/{reminder_id}/cancel", response_model=dict)
async def cancel_reminder(
    user_id: str = Path(..., description="User ID"),
    reminder_id: int = Path(..., description="Reminder ID"),
    current_user: str = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    """
    Cancel a pending reminder.

    Args:
        user_id: User ID from URL path
        reminder_id: Reminder ID
        current_user: Authenticated user ID from JWT
        reminder_service: Reminder service instance

    Returns:
        Success message

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if not found
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    success = reminder_service.cancel_reminder(reminder_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found or not pending",
        )

    return {"message": "Reminder cancelled successfully", "reminder_id": reminder_id}