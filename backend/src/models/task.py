"""
Task model for todo items
Each task belongs to one user (many-to-one relationship)
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    """Task entity with user association"""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
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
