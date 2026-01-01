"""
Conversation and Message models for Phase III AI Chatbot

Defines SQLModel entities for chat conversations and messages.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message sender role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"


class Conversation(SQLModel, table=True):
    """
    Represents a chat session between a user and the AI assistant.

    Lifecycle:
    - Active: 90 days from last update
    - Archived: 1 year after becoming inactive
    - Deleted: Permanent removal after archive period
    """
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def touch(self):
        """Update timestamp when new message added"""
        self.updated_at = datetime.utcnow()


class Message(SQLModel, table=True):
    """
    Individual user or assistant message within a conversation.

    Messages are immutable after creation (no UPDATE operations).
    Content validation: user messages limited to 1000 chars, assistant up to 10000.
    """
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(sa_column_kwargs={"nullable": False})  # Store as string, validate with MessageRole
    content: str = Field(max_length=10000)  # Allow longer assistant responses
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __init__(self, **data):
        """Validate user message length and role on initialization"""
        super().__init__(**data)

        # Validate role
        if self.role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
            raise ValueError(f"Invalid role: {self.role}. Must be 'user' or 'assistant'")

        # Validate user message length
        if self.role == MessageRole.USER.value and len(self.content) > 1000:
            raise ValueError("User messages limited to 1000 characters")
