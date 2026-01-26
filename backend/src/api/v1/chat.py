"""
Chat API Endpoints for Phase III AI Chatbot

RESTful API for AI-powered chat interface with JWT authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from sqlmodel import Session
import uuid

from src.api.deps import get_current_user
from src.models.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService
from src.services.queue_service import RateLimitError, QueueTimeoutError
from src.config.logging import logger
from src.db import get_session


router = APIRouter()


def get_chat_service(db: Session = Depends(get_session)) -> ChatService:
    """Dependency to get ChatService instance"""
    return ChatService(db)


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    user_id: str = Path(..., description="User ID"),
    request: ChatRequest = ...,
    current_user: str = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
    http_request: Request = None
):
    """
    Send message to AI chatbot and get response.

    This endpoint is stateless - all conversation history loaded from database.
    Integrates with OpenAI Agents SDK and MCP tools for task operations.

    Args:
        user_id: User ID from URL path (must match authenticated user)
        request: ChatRequest with conversation_id and message
        current_user: Authenticated user ID from JWT token
        chat_service: Chat service instance
        http_request: FastAPI request object for correlation ID

    Returns:
        ChatResponse with conversation_id, assistant response, and tool_calls

    Raises:
        HTTPException:
            - 400: Invalid request (empty message, invalid conversation_id)
            - 401: Unauthorized (invalid JWT token)
            - 403: Forbidden (user_id doesn't match authenticated user)
            - 429: Rate limit exceeded (OpenAI API)
            - 500: Internal server error
    """
    # Generate correlation ID for request tracing
    correlation_id = str(uuid.uuid4())

    logger.info("chat_request_received",
               correlation_id=correlation_id,
               user_id=user_id,
               conversation_id=request.conversation_id,
               message_length=len(request.message))

    # Authorization: user_id must match authenticated user
    if user_id != current_user:
        logger.warning("chat_authorization_failed",
                      correlation_id=correlation_id,
                      requested_user_id=user_id,
                      authenticated_user_id=current_user)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user"
        )

    try:
        # Process chat message through service
        response = await chat_service.process_chat_message(
            user_id=user_id,
            request=request,
            correlation_id=correlation_id
        )

        logger.info("chat_request_success",
                   correlation_id=correlation_id,
                   user_id=user_id,
                   conversation_id=response.conversation_id,
                   tool_calls_count=len(response.tool_calls))

        return response

    except ValueError as e:
        # Validation errors (invalid conversation_id, message format)
        logger.warning("chat_validation_error",
                      correlation_id=correlation_id,
                      user_id=user_id,
                      error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except RateLimitError as e:
        # OpenAI rate limit exceeded after retries
        logger.error("chat_rate_limit_error",
                    correlation_id=correlation_id,
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI service rate limit exceeded. Please try again in a moment."
        )

    except QueueTimeoutError as e:
        # Request timeout (> 30 seconds)
        logger.error("chat_timeout_error",
                    correlation_id=correlation_id,
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timeout. Please try again."
        )

    except Exception as e:
        # Unexpected errors
        import traceback
        error_detail = traceback.format_exc()
        logger.error("chat_internal_error",
                    correlation_id=correlation_id,
                    user_id=user_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=error_detail)

        # Include more specific details for known database errors if possible
        detail = "An unexpected error occurred. Please try again later."
        if "Mapping" in str(e) or "Table" in str(e):
             detail = f"Database error: {str(e)}"

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
