"""
Task CRUD Endpoints
RESTful API for task operations with JWT authentication including advanced features
like priorities, tags, due dates, sorting, and search capabilities.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Request
from sqlmodel import Session
from datetime import datetime

from src.api.deps import get_current_user
from src.schemas.task_schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from src.services.task_service import TaskService
from src.db import get_session

logger = logging.getLogger(__name__)

router = APIRouter()


def get_task_service(db: Session = Depends(get_session)) -> TaskService:
    """Dependency to get TaskService instance"""
    return TaskService(db)


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str = Path(..., description="User ID"),
    status_param: Optional[str] = Query(None, pattern="^(all|pending|completed)$"),
    priority: Optional[str] = Query(None, pattern="^(low|medium|high|urgent)$"),
    sort_by: Optional[str] = Query("created_at", pattern="^(due_date|priority|created_at|title)$"),
    sort_order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    limit: Optional[int] = Query(20, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    List all tasks for the authenticated user with filtering, sorting, and pagination.

    Args:
        user_id: User ID from URL path
        status_param: Filter by status ('all', 'pending', 'completed')
        priority: Filter by priority ('low', 'medium', 'high', 'urgent')
        sort_by: Sort by field ('due_date', 'priority', 'created_at', 'title')
        sort_order: Sort order ('asc' or 'desc')
        limit: Number of tasks to return (1-100, default 20)
        offset: Number of tasks to skip for pagination
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

    Returns:
        TaskListResponse with tasks array and count

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )
    try:
        # Apply status filter when calling the service method
        status_filter = status_param if status_param and status_param != 'all' else None
        tasks = task_service.get_tasks_by_user(current_user, status_filter=status_filter)

        # Apply sorting
        if sort_by == "due_date":
            if sort_order == "asc":
                tasks = sorted(tasks, key=lambda x: (x.due_date is None, x.due_date), reverse=False)
            else:
                tasks = sorted(tasks, key=lambda x: (x.due_date is None, x.due_date), reverse=True)
        elif sort_by == "priority":
            if sort_order == "asc":
                tasks = sorted(tasks, key=lambda x: x.priority.value, reverse=False)
            else:
                tasks = sorted(tasks, key=lambda x: x.priority.value, reverse=True)
        elif sort_by == "title":
            if sort_order == "asc":
                tasks = sorted(tasks, key=lambda x: x.title.lower(), reverse=False)
            else:
                tasks = sorted(tasks, key=lambda x: x.title.lower(), reverse=True)
        else:  # sort_by == "created_at" (default)
            # Apply the sort order to creation date
            if sort_order == "asc":
                tasks = sorted(tasks, key=lambda x: x.created_at, reverse=False)
            else:
                tasks = sorted(tasks, key=lambda x: x.created_at, reverse=True)

        # Apply priority filter after sorting
        if priority:
            tasks = [task for task in tasks if task.priority.value == priority]

        # Apply pagination
        start_idx = offset
        end_idx = start_idx + limit
        paginated_tasks = tasks[start_idx:end_idx]

        return TaskListResponse(
            tasks=[TaskResponse.from_orm(t) for t in paginated_tasks],
            count=len(tasks)
        )
    except Exception as e:
        # Log the exception for debugging
        logger.error(f"Error in list_tasks: {str(e)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}",
        )


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    user_id: str = Path(..., description="User ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Create a new task for the authenticated user with advanced features.

    Args:
        request: HTTP request with JSON body
        user_id: User ID from URL path
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

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
        task_data = TaskCreate(**body)

        task = task_service.create_task(
            user_id=current_user,
            title=task_data.title,
            description=task_data.description,
            priority=getattr(task_data, 'priority', 'medium'),
            tags=getattr(task_data, 'tags', []),
            category=getattr(task_data, 'category', None),
            due_date=getattr(task_data, 'due_date', None)
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
            detail=f"Failed to create task: {str(e)}",
        )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Get a specific task by ID.

    Args:
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

    Returns:
        TaskResponse

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if task not found
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )
    task = task_service.get_task(task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.from_orm(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    request: Request,
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Update task with advanced features.

    Args:
        request: HTTP request with JSON body
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

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
        task_data = TaskUpdate(**body)

        task = task_service.update_task(
            task_id=task_id,
            user_id=current_user,
            title=task_data.title,
            description=task_data.description,
            priority=getattr(task_data, 'priority', None),
            tags=getattr(task_data, 'tags', None),
            category=getattr(task_data, 'category', None),
            due_date=getattr(task_data, 'due_date', None)
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
            detail=f"Failed to update task: {str(e)}",
        )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Toggle task completion status (pending ↔ completed).

    Args:
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

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

    task = task_service.complete_task(task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.from_orm(task)


@router.patch("/{user_id}/tasks/{task_id}/incomplete", response_model=TaskResponse)
async def mark_task_incomplete(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Mark a task as incomplete.

    Args:
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

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

    task = task_service.uncomplete_task(task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.from_orm(task)


@router.patch("/{user_id}/tasks/{task_id}/priority", response_model=TaskResponse)
async def update_task_priority(
    request: Request,
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Update the priority of a task.

    Args:
        request: HTTP request with JSON body containing priority
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

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
        priority = body.get('priority')

        if not priority:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Priority is required",
            )

        task = task_service.update_task_priority(task_id, current_user, priority)
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
            detail=f"Failed to update task priority: {str(e)}",
        )


@router.patch("/{user_id}/tasks/{task_id}/tags", response_model=TaskResponse)
async def update_task_tags(
    request: Request,
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Add tags to a task.

    Args:
        request: HTTP request with JSON body containing tags
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

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
        tags = body.get('tags', [])

        if not tags:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tags list is required",
            )

        task = task_service.add_tags_to_task(task_id, current_user, tags)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return TaskResponse.from_orm(task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task tags: {str(e)}",
        )


@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Delete a task permanently.

    Args:
        user_id: User ID from URL path
        task_id: Task ID
        current_user: Authenticated user ID from JWT
        task_service: Task service instance

    Returns:
        Success message with deleted task ID

    Raises:
        HTTPException: 403 if user_id mismatch, 404 if not found
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )
    deleted = task_service.delete_task(task_id, current_user)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return {"message": "Task deleted successfully", "task_id": task_id}
