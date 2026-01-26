"""
Recurring Task Endpoints
RESTful API for recurring task operations with JWT authentication.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from sqlmodel import Session

from src.api.deps import get_current_user
from src.schemas.task_schemas import RecurringTaskCreate, TaskResponse
from src.services.recurring_task_service import RecurringTaskService
from src.db import get_session

router = APIRouter()


def get_recurring_task_service(db: Session = Depends(get_session)) -> RecurringTaskService:
    """Dependency to get RecurringTaskService instance"""
    return RecurringTaskService(db)


@router.post("/{user_id}/recurring-tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_task(
    request: Request,
    user_id: str = Path(..., description="User ID"),
    current_user: str = Depends(get_current_user),
    recurring_task_service: RecurringTaskService = Depends(get_recurring_task_service),
):
    """
    Create a new recurring task for the authenticated user.

    Args:
        request: HTTP request with JSON body
        user_id: User ID from URL path
        current_user: Authenticated user ID from JWT
        recurring_task_service: Recurring task service instance

    Returns:
        Created TaskResponse

    Raises:
        HTTPException: 403 if user_id mismatch, 422 for validation errors
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )
    try:
        body = await request.json()
        recurring_task_data = RecurringTaskCreate(**body)

        task = recurring_task_service.create_recurring_task(
            user_id=current_user,
            title=recurring_task_data.title,
            description=recurring_task_data.description,
            priority=getattr(recurring_task_data, 'priority', 'medium'),
            category=getattr(recurring_task_data, 'category', None),
            due_date=getattr(recurring_task_data, 'due_date', None),
            recurrence_pattern=recurring_task_data.recurrence_pattern,
            first_occurrence_date=getattr(recurring_task_data, 'first_occurrence_date', None)
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
            detail=f"Failed to create recurring task: {str(e)}",
        )


@router.patch("/{user_id}/recurring-tasks/{task_id}/pattern", response_model=TaskResponse)
async def update_recurring_task_pattern(
    request: Request,
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    update_future_tasks: bool = False,
    current_user: str = Depends(get_current_user),
    recurring_task_service: RecurringTaskService = Depends(get_recurring_task_service),
):
    """
    Update the recurrence pattern of a recurring task.

    Args:
        request: HTTP request with JSON body containing new pattern
        user_id: User ID from URL path
        task_id: Task ID
        update_future_tasks: Whether to update all future occurrences
        current_user: Authenticated user ID from JWT
        recurring_task_service: Recurring task service instance

    Returns:
        Updated TaskResponse

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if not found, 422 for validation errors
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    try:
        body = await request.json()
        recurrence_pattern = body.get('recurrence_pattern')

        if not recurrence_pattern:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Recurrence pattern is required",
            )

        task = recurring_task_service.update_recurring_task_pattern(
            task_id, recurrence_pattern, update_future_tasks
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring task not found",
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
            detail=f"Failed to update recurring task pattern: {str(e)}",
        )


@router.post("/{user_id}/recurring-tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_recurring_task_and_generate_next(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    recurring_task_service: RecurringTaskService = Depends(get_recurring_task_service),
):
    """
    Complete a recurring task and generate the next occurrence.

    Args:
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        recurring_task_service: Recurring task service instance

    Returns:
        Updated TaskResponse

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if not found
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    task = recurring_task_service.complete_recurring_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found",
        )

    return TaskResponse.from_orm(task)