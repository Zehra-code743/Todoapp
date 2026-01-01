"""
OpenAI Agent initialization service for Phase III AI Chatbot

Configures OpenAI Agents SDK with gpt-4o-mini model.
Integrates with MCP server for tool execution.
"""
from openai import AsyncOpenAI
import httpx
from typing import List, Dict, Any
from config.logging import logger
import os
from src.config import settings


# Model configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Lazy client initialization
_client = None


def get_client() -> AsyncOpenAI:
    """Get or create OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        api_key = settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Manually create httpx client to avoid 'proxies' argument incompatibility
        # in some versions of openai-python and httpx
        http_client = httpx.AsyncClient()
        _client = AsyncOpenAI(api_key=api_key, http_client=http_client)
    return _client


# Agent system prompt with intent recognition patterns
AGENT_SYSTEM_PROMPT = """You are a helpful AI assistant for a todo application. You can help users manage their tasks through natural conversation.

Available operations:
- **Create tasks**: When users describe something they need to do (e.g., "I need to buy groceries tomorrow", "remind me to call mom")
- **View tasks**: When users ask about their tasks (e.g., "what do I need to do?", "show my tasks", "what's pending?")
- **Complete tasks**: When users mark tasks done (e.g., "mark groceries as done", "I finished the meeting")
- **Update tasks**: When users want to change task details (e.g., "change task title to...", "update the description")
- **Delete tasks**: When users want to remove tasks (e.g., "delete the groceries task", "remove that item")

Guidelines:
- Be conversational and natural
- Extract task information from natural language
- Ask for clarification when task references are ambiguous
- Confirm actions after completing them
- Use the MCP tools to perform actual operations
"""


async def create_chat_completion(
    messages: List[Dict[str, str]],
    tools: List[Dict[str, Any]] = None,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Create a chat completion using OpenAI API with optional tool calls.

    Args:
        messages: List of message dicts with 'role' and 'content'
        tools: Optional list of MCP tool schemas
        user_id: User ID for logging/tracking

    Returns:
        Dict with response content and tool_calls (if any)

    Raises:
        Exception: On API errors
    """
    logger.info("openai_request_starting",
                user_id=user_id,
                message_count=len(messages),
                tools_available=len(tools) if tools else 0,
                model=OPENAI_MODEL)

    try:
        # Build request parameters
        request_params = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                *messages
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        # Add tools if provided
        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"

        # Make API request
        client = get_client()
        response = await client.chat.completions.create(**request_params)

        # Extract response
        message = response.choices[0].message
        result = {
            "content": message.content or "",
            "tool_calls": []
        }

        # Extract tool calls if present
        if hasattr(message, "tool_calls") and message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
                for tc in message.tool_calls
            ]

        logger.info("openai_request_success",
                   user_id=user_id,
                   response_length=len(result["content"]),
                   tool_calls_count=len(result["tool_calls"]),
                   model=OPENAI_MODEL)

        return result

    except Exception as e:
        logger.error("openai_request_failed",
                    user_id=user_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    model=OPENAI_MODEL)
        raise


def validate_agent_config():
    """
    Validate that required environment variables are set.

    Raises:
        ValueError: If OPENAI_API_KEY is missing or placeholder
    """
    api_key = settings.openai_api_key

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    if api_key.startswith("sk-proj-xxxxx"):
        raise ValueError(
            "OPENAI_API_KEY is still using placeholder value. "
            "Please set a real OpenAI API key in backend/.env"
        )

    logger.info("agent_config_validated",
               model=OPENAI_MODEL,
               api_key_prefix=api_key[:10] + "...")


# Validate on import (only if API key is set)
if settings.openai_api_key:
    try:
        validate_agent_config()
    except ValueError as e:
        logger.warning("agent_config_validation_failed",
                      error=str(e),
                      message="Agent will not work until OPENAI_API_KEY is set")
else:
    logger.warning("openai_api_key_not_set",
                  message="OPENAI_API_KEY not configured - chatbot will not work")
