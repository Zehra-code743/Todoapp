"""
Pydantic schemas for Task CRUD operations
Request and response models for API endpoints
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class TaskCreate(BaseModel):
    """Request body for creating a new task"""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Optional task description"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {"title": "Buy groceries", "description": "Milk, eggs, bread"}
        }


class TaskUpdate(BaseModel):
    """Request body for updating a task"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError("Title cannot be empty")
        return v.strip() if v else None

    class Config:
        json_schema_extra = {
            "example": {"title": "Buy groceries and fruits", "description": "Updated list"}
        }


class TaskResponse(BaseModel):
    """Response model for a single task"""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_abc123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2025-12-26T10:30:00Z",
                "updated_at": "2025-12-26T10:30:00Z",
            }
        }


class TaskListResponse(BaseModel):
    """Response model for listing tasks"""

    tasks: List[TaskResponse]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "user_id": "user_abc123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2025-12-26T10:30:00Z",
                        "updated_at": "2025-12-26T10:30:00Z",
                    }
                ],
                "count": 1,
            }
        }
