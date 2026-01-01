"""
Chat API Request/Response models for Phase III AI Chatbot

Pydantic models per contracts/chat-api.yaml specification.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """
    Request payload for POST /api/{user_id}/chat endpoint.

    Schema from chat-api.yaml ChatRequest component.
    """
    conversation_id: Optional[int] = Field(
        default=None,
        description="ID of existing conversation (null to create new conversation)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User's message in natural language"
    )

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty or whitespace-only"""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversation_id": None,
                    "message": "I need to buy groceries tomorrow"
                },
                {
                    "conversation_id": 42,
                    "message": "Show my pending tasks"
                }
            ]
        }
    }


class ToolCall(BaseModel):
    """
    MCP tool invocation record.

    Schema from chat-api.yaml ToolCall component.
    """
    tool_name: str = Field(
        ...,
        description="Name of the MCP tool invoked (e.g., 'add_task', 'list_tasks')"
    )
    parameters: Dict[str, Any] = Field(
        ...,
        description="Parameters passed to the tool"
    )
    result: Dict[str, Any] = Field(
        ...,
        description="Result returned by the tool"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tool_name": "add_task",
                "parameters": {
                    "user_id": "usr_2a1b3c4d5e6f7g8h",
                    "title": "Buy groceries"
                },
                "result": {
                    "task_id": 123,
                    "status": "created",
                    "title": "Buy groceries"
                }
            }
        }
    }


class ChatResponse(BaseModel):
    """
    Response payload for POST /api/{user_id}/chat endpoint.

    Schema from chat-api.yaml ChatResponse component.
    """
    conversation_id: int = Field(
        ...,
        description="ID of the conversation (newly created or existing)"
    )
    response: str = Field(
        ...,
        description="AI assistant's natural language response"
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="MCP tools invoked during message processing"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "conversation_id": 42,
                "response": "I've added 'Buy groceries' to your task list.",
                "tool_calls": [
                    {
                        "tool_name": "add_task",
                        "parameters": {
                            "user_id": "usr_2a1b3c4d5e6f7g8h",
                            "title": "Buy groceries"
                        },
                        "result": {
                            "task_id": 123,
                            "status": "created",
                            "title": "Buy groceries"
                        }
                    }
                ]
            }
        }
    }
