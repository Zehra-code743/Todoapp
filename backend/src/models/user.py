"""
User model for authentication and user management
Managed by Better Auth on frontend, stored in database
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """User entity with authentication fields"""

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(min_length=2, max_length=100)
    password_hash: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_abc123",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2025-12-26T10:30:00Z",
                "updated_at": "2025-12-26T10:30:00Z",
            }
        }
