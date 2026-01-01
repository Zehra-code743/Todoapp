"""
Quick test to verify Phase III setup is working
"""
import sys
import os

print("=" * 60)
print("Phase III Setup Verification")
print("=" * 60)

# Test 1: Import all Phase III modules
print("\n1. Testing imports...")
try:
    from models.conversation import Conversation, Message, MessageRole
    from models.chat import ChatRequest, ChatResponse, ToolCall
    from config.logging import logger
    from services.queue_service import process_with_backoff
    from services.agent_service import create_chat_completion, validate_agent_config
    from services.chat_service import ChatService
    from mcp_tools.mcp_server import mcp_server, initialize_mcp_server
    from mcp_tools.tools.add_task import add_task, ADD_TASK_SCHEMA
    print("   [OK] All imports successful")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Check database tables exist
print("\n2. Checking database tables...")
try:
    from src.db import engine
    from sqlmodel import Session, select

    with Session(engine) as session:
        # Try to query conversations table
        result = session.exec(select(Conversation).limit(1))
        result.all()
        print("   [OK] Conversations table exists")

        # Try to query messages table
        result = session.exec(select(Message).limit(1))
        result.all()
        print("   [OK] Messages table exists")
except Exception as e:
    print(f"   [FAIL] Database check failed: {e}")
    print("   Note: Run backend/run_migration.py if tables don't exist")

# Test 3: Validate agent configuration
print("\n3. Validating agent configuration...")
try:
    validate_agent_config()
    print("   [OK] Agent configuration valid")
except ValueError as e:
    print(f"   [WARN] Agent config warning: {e}")
    print("   Note: Set OPENAI_API_KEY in backend/.env to enable chatbot")

# Test 4: Check MCP tool registration
print("\n4. Checking MCP tool schema...")
try:
    assert ADD_TASK_SCHEMA["name"] == "add_task"
    assert "input_schema" in ADD_TASK_SCHEMA
    assert "type" in ADD_TASK_SCHEMA["input_schema"]
    print("   [OK] MCP add_task schema valid")
except Exception as e:
    print(f"   [FAIL] MCP schema check failed: {e}")

# Test 5: Verify chat models
print("\n5. Verifying Pydantic models...")
try:
    # Test ChatRequest validation
    req = ChatRequest(conversation_id=None, message="Test message")
    assert req.message == "Test message"

    # Test ChatResponse
    resp = ChatResponse(
        conversation_id=1,
        response="Test response",
        tool_calls=[]
    )
    assert resp.conversation_id == 1
    print("   [OK] Chat models validation successful")
except Exception as e:
    print(f"   [FAIL] Model validation failed: {e}")

print("\n" + "=" * 60)
print("Setup Verification Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Set OPENAI_API_KEY in backend/.env (required for chatbot)")
print("2. Start backend: cd backend && uvicorn src.main:app --reload")
print("3. Start frontend: cd frontend && npm run dev")
print("4. Test: Navigate to http://localhost:3000/chat")
print("5. Try: 'I need to buy groceries tomorrow'")
print("=" * 60)
