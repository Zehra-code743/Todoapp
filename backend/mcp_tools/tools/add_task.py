"""
MCP Tool: add_task

Creates a new task for the user via natural language AI agent.
Wraps existing TaskService.create_task() from Phase II.
"""
from typing import Dict, Any, Optional
from sqlmodel import Session
from src.services.task_service import TaskService
from src.config.logging import logger


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    db_session: Session = None
) -> Dict[str, Any]:
    """
    MCP tool to create a new task for the user.

    Args:
        user_id: ID of the user creating the task
        title: Task title (1-200 characters)
        description: Optional task description (max 1000 characters)
        db_session: Database session (injected by caller)

    Returns:
        Dict with task_id, status, and title confirmation

    Raises:
        ValueError: If validation fails
        Exception: If database operation fails
    """
    logger.info("mcp_add_task_called",
               user_id=user_id,
               title_length=len(title),
               has_description=description is not None)

    try:
        # Validation (redundant with TaskService but required by MCP contract)
        if not title or len(title.strip()) < 1:
            raise ValueError("Title must be 1-200 characters")
        if len(title) > 200:
            raise ValueError("Title must be 1-200 characters")
        if description and len(description) > 1000:
            raise ValueError("Description exceeds 1000 characters")

        # Create task using existing service
        task_service = TaskService(db_session)
        task = task_service.create_task(
            user_id=user_id,
            title=title,
            description=description
        )

        result = {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

        logger.info("mcp_add_task_success",
                   user_id=user_id,
                   task_id=task.id,
                   title=task.title)

        return result

    except ValueError as e:
        logger.warning("mcp_add_task_validation_error",
                      user_id=user_id,
                      error=str(e))
        raise

    except Exception as e:
        logger.error("mcp_add_task_failed",
                    user_id=user_id,
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise


# MCP tool metadata for registration
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task for the user",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "ID of the user creating the task"
            },
            "title": {
                "type": "string",
                "description": "Task title (1-200 characters)"
            },
            "description": {
                "type": "string",
                "description": "Optional task description (max 1000 characters)"
            }
        },
        "required": ["user_id", "title"]
    }
}
