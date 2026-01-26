"""
Chat Service for Phase III AI Chatbot

Orchestrates conversation management, message processing, OpenAI agent,
and MCP tool execution.
"""
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime
import json

from src.models.conversation import Conversation, Message, MessageRole
from src.models.chat import ChatRequest, ChatResponse, ToolCall
from src.services.agent_service import create_chat_completion
from src.services.queue_service import process_with_backoff, RateLimitError
from mcp_tools.tools.add_task import add_task
from src.config.logging import logger
import uuid


class ChatService:
    """Service for chat conversation and message operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[int] = None
    ) -> Conversation:
        """
        Get existing conversation or create new one.

        Args:
            user_id: User ID
            conversation_id: Optional existing conversation ID

        Returns:
            Conversation object

        Raises:
            ValueError: If conversation_id doesn't exist or doesn't belong to user
        """
        if conversation_id:
            # Load existing conversation
            query = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = self.db.exec(query).first()

            if not conversation:
                raise ValueError(
                    f"Conversation {conversation_id} not found or unauthorized"
                )

            logger.info("conversation_loaded",
                       conversation_id=conversation_id,
                       user_id=user_id)

            return conversation
        else:
            # Create new conversation
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            logger.info("conversation_created",
                       conversation_id=conversation.id,
                       user_id=user_id)

            return conversation

    def load_conversation_history(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> List[Dict[str, str]]:
        """
        Load last N messages from conversation as OpenAI message format.

        Args:
            conversation_id: Conversation ID
            limit: Max messages to load (default: 50)

        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit)

        messages = self.db.exec(query).all()

        # Reverse to chronological order (oldest first)
        messages = list(reversed(messages))

        # Convert to OpenAI format
        history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]

        logger.info("conversation_history_loaded",
                   conversation_id=conversation_id,
                   message_count=len(history))

        return history

    def save_message(
        self,
        conversation_id: int,
        user_id: str,
        role: str,
        content: str
    ) -> Message:
        """
        Save message to database.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            role: Message role string ("user" or "assistant")
            content: Message content

        Returns:
            Saved Message object
        """
        # Validate role
        if role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # Update conversation timestamp (trigger handles this in DB,
        # but we also update the object for consistency)
        conversation = self.db.get(Conversation, conversation_id)
        if conversation:
            conversation.touch()
            self.db.add(conversation)
            self.db.commit()

        logger.info("message_saved",
                   conversation_id=conversation_id,
                   message_id=message.id,
                   role=role,
                   content_length=len(content))

        return message

    async def process_chat_message(
        self,
        user_id: str,
        request: ChatRequest,
        correlation_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Process chat message: manage conversation, call OpenAI agent,
        execute MCP tools, save messages.

        Args:
            user_id: User ID
            request: ChatRequest with conversation_id and message
            correlation_id: Optional correlation ID for logging

        Returns:
            ChatResponse with response and tool_calls

        Raises:
            ValueError: If validation fails
            RateLimitError: If OpenAI rate limit exceeded after retries
        """
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        logger.info("chat_message_processing_start",
                   correlation_id=correlation_id,
                   user_id=user_id,
                   conversation_id=request.conversation_id,
                   message_length=len(request.message))

        try:
            # 1. Get or create conversation
            conversation = self.get_or_create_conversation(
                user_id=user_id,
                conversation_id=request.conversation_id
            )

            # 2. Save user message
            self.save_message(
                conversation_id=conversation.id,
                user_id=user_id,
                role=MessageRole.USER.value,  # Use enum value (string)
                content=request.message
            )

            # 3. Load conversation history
            history = self.load_conversation_history(conversation.id)

            # 4. Add current message to history
            history.append({
                "role": "user",
                "content": request.message
            })

            # 5. Call OpenAI agent with MCP tool schemas and rate limiting
            tool_schemas = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Create a new task for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Task title"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Optional task description"
                                }
                            },
                            "required": ["title"]
                        }
                    }
                }
            ]

            ai_response = await process_with_backoff(
                create_chat_completion,
                messages=history,
                tools=tool_schemas,
                user_id=user_id
            )

            # 6. Execute MCP tool calls if present
            tool_calls_result = []
            if ai_response.get("tool_calls"):
                for tc in ai_response["tool_calls"]:
                    if tc["name"] == "add_task":
                        args = json.loads(tc["arguments"])
                        result = await add_task(
                            user_id=user_id,
                            title=args.get("title"),
                            description=args.get("description"),
                            db_session=self.db
                        )
                        tool_calls_result.append(ToolCall(
                            tool_name="add_task",
                            parameters={"user_id": user_id, **args},
                            result=result
                        ))

            # 7. Save assistant response
            assistant_content = ai_response.get("content", "")
            self.save_message(
                conversation_id=conversation.id,
                user_id=user_id,
                role=MessageRole.ASSISTANT.value,  # Use enum value (string)
                content=assistant_content
            )

            # 8. Build response
            response = ChatResponse(
                conversation_id=conversation.id,
                response=assistant_content,
                tool_calls=tool_calls_result
            )

            logger.info("chat_message_processing_success",
                       correlation_id=correlation_id,
                       user_id=user_id,
                       conversation_id=conversation.id,
                       tool_calls_count=len(tool_calls_result))

            return response

        except RateLimitError as e:
            logger.error("chat_rate_limit_exceeded",
                        correlation_id=correlation_id,
                        user_id=user_id,
                        error=str(e))
            raise

        except Exception as e:
            logger.error("chat_message_processing_failed",
                        correlation_id=correlation_id,
                        user_id=user_id,
                        error_type=type(e).__name__,
                        error_message=str(e))
            raise
