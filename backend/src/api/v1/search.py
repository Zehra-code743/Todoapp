"""
Search Endpoints
RESTful API for search and filter operations with JWT authentication.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from datetime import datetime

from src.api.deps import get_current_user
from src.schemas.task_schemas import TaskListResponse
from src.services.search_service import SearchService
from src.db import get_session

router = APIRouter()


def get_search_service(db: Session = Depends(get_session)) -> SearchService:
    """Dependency to get SearchService instance"""
    return SearchService(db)


@router.get("/tasks", response_model=TaskListResponse)
async def search_tasks(
    current_user: str = Depends(get_current_user),
    keyword: Optional[str] = Query(None, description="Keyword to search in title or description"),
    status: Optional[str] = Query(None, regex="^(all|pending|completed)$", description="Filter by status"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high|urgent)$", description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    due_date_start: Optional[datetime] = Query(None, description="Start date for due date range"),
    due_date_end: Optional[datetime] = Query(None, description="End date for due date range"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination"),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Search tasks with various filters and keywords.

    Args:
        current_user: Authenticated user ID from JWT
        keyword: Keyword to search in title or description
        status: Filter by status ('all', 'pending', 'completed')
        priority: Filter by priority ('low', 'medium', 'high', 'urgent')
        tag: Filter by tag
        due_date_start: Start date for due date range
        due_date_end: End date for due date range
        limit: Number of results to return (1-100, default 20)
        offset: Number of results to skip for pagination
        search_service: Search service instance

    Returns:
        TaskListResponse with matching tasks and count

    Raises:
        HTTPException: 422 for validation errors
    """
    try:
        # Convert single tag to list format for the service
        tags = [tag] if tag else []

        tasks = search_service.search_tasks(
            user_id=current_user,
            keyword=keyword,
            status=status,
            priority=priority,
            tags=tags,
            due_date_start=due_date_start,
            due_date_end=due_date_end,
            limit=limit,
            offset=offset
        )

        # We need to get the total count separately for the response
        # This would require a separate count method in the search service
        # For now, we'll return the tasks we have
        from src.services.task_service import TaskService
        with get_session() as db:
            task_service = TaskService(db)
            total_count = task_service.get_tasks_count_by_user(current_user)

        # Create response objects
        from src.schemas.task_schemas import TaskResponse
        task_responses = [TaskResponse.from_orm(task) for task in tasks]

        return TaskListResponse(tasks=task_responses, count=len(tasks))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search tasks: {str(e)}",
        )


@router.get("/tasks/statistics", response_model=dict)
async def get_task_statistics(
    current_user: str = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Get task statistics for the authenticated user.

    Args:
        current_user: Authenticated user ID from JWT
        search_service: Search service instance

    Returns:
        Dictionary with task statistics
    """
    try:
        stats = search_service.get_tasks_statistics(current_user)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task statistics: {str(e)}",
        )


@router.get("/tags", response_model=list)
async def get_user_tags(
    current_user: str = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Get all tags used by the authenticated user.

    Args:
        current_user: Authenticated user ID from JWT
        search_service: Search service instance

    Returns:
        List of unique tags used by the user
    """
    try:
        tags = search_service.get_all_tags_for_user(current_user)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user tags: {str(e)}",
        )


@router.get("/tasks/priorities", response_model=list)
async def get_tasks_by_priority_endpoint(
    priority: str = Query(..., regex="^(low|medium|high|urgent)$", description="Priority to filter by"),
    current_user: str = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Get tasks filtered by priority.

    Args:
        priority: Priority level to filter by ('low', 'medium', 'high', 'urgent')
        current_user: Authenticated user ID from JWT
        search_service: Search service instance

    Returns:
        List of tasks with the specified priority
    """
    try:
        tasks = search_service.get_tasks_by_priority(current_user, priority)
        from src.schemas.task_schemas import TaskResponse
        return [TaskResponse.from_orm(task) for task in tasks]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tasks by priority: {str(e)}",
        )


@router.get("/tasks/categories", response_model=list)
async def get_tasks_by_category_endpoint(
    category: str = Query(..., description="Category to filter by"),
    current_user: str = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Get tasks filtered by category.

    Args:
        category: Category to filter by
        current_user: Authenticated user ID from JWT
        search_service: Search service instance

    Returns:
        List of tasks with the specified category
    """
    try:
        tasks = search_service.get_tasks_by_category(current_user, category)
        from src.schemas.task_schemas import TaskResponse
        return [TaskResponse.from_orm(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tasks by category: {str(e)}",
        )