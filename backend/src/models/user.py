"""
User model for authentication and user management
Includes timezone information as required by the Advanced Todo Features specification.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class User(SQLModel, table=True):
    """User entity with authentication and timezone information"""

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(min_length=2, max_length=100)
    password_hash: str = Field()
    timezone: str = Field(default="UTC", max_length=50)  # Timezone for the user
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_abc123",
                "email": "user@example.com",
                "name": "John Doe",
                "timezone": "America/New_York",
                "created_at": "2025-12-26T10:30:00Z",
                "updated_at": "2025-12-26T10:30:00Z",
            }
        }
