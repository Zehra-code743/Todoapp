"""
Task CRUD Endpoints
RESTful API for task operations with JWT authentication
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Request
from sqlmodel import Session

from src.api.deps import get_current_user
from src.schemas.task_schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from src.services.task_service import TaskService
from src.db import get_session

router = APIRouter()


def get_task_service(db: Session = Depends(get_session)) -> TaskService:
    """Dependency to get TaskService instance"""
    return TaskService(db)


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str = Path(..., description="User ID"),
    status_filter: Optional[str] = Query(None, alias="status", regex="^(all|pending|completed)$"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    List all tasks for the authenticated user

    Args:
        user_id: User ID from URL path
        status_filter: Optional filter ('all', 'pending', 'completed')
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
        tasks = task_service.get_tasks_by_user(current_user, status_filter)
        return TaskListResponse(tasks=[TaskResponse.from_orm(t) for t in tasks], count=len(tasks))
    except Exception as e:
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
    Create a new task for the authenticated user

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
    Get a specific task by ID

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
    task = task_service.get_task_by_id(task_id, current_user)
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
    Update task title and/or description

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
    Toggle task completion status (pending ↔ completed)

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
    task = task_service.toggle_task_completion(task_id, current_user)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.from_orm(task)


@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """
    Delete a task permanently

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
