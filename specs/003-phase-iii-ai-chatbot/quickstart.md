# Quickstart Guide: Phase III - Todo AI Chatbot

**Feature**: Phase III - Todo AI Chatbot
**Audience**: Developers implementing this feature
**Prerequisites**: Phase II implementation complete (FastAPI backend + Next.js frontend + PostgreSQL database)

---

## Overview

This guide provides a step-by-step walkthrough for implementing the AI chatbot feature. Follow the sequence to ensure proper setup and integration.

---

## Prerequisites Checklist

Before starting implementation, ensure you have:

- [ ] Phase II Todo web application running locally
- [ ] PostgreSQL database accessible (Neon or local)
- [ ] OpenAI API key (get from https://platform.openai.com/api-keys)
- [ ] Node.js 18+ and Python 3.11+ installed
- [ ] Git repository on branch `003-phase-iii-ai-chatbot`

---

## Step 1: Environment Setup

### 1.1 Install Backend Dependencies

```bash
cd backend

# Add to requirements.txt or install directly
pip install openai==1.0.0+          # OpenAI Agents SDK
pip install mcp==0.1.0+              # Official MCP SDK
pip install structlog==23.0.0+       # Structured logging

# Install all dependencies
pip install -r requirements.txt
```

### 1.2 Install Frontend Dependencies

```bash
cd frontend

# Add OpenAI ChatKit
npm install @openai/chatkit@latest

# Or using yarn
yarn add @openai/chatkit
```

### 1.3 Set Environment Variables

Create or update `.env` file in backend directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx  # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini               # Model to use

# MCP Server Configuration
MCP_SERVER_PORT=3001                   # Port for MCP server

# Database (existing from Phase II)
DATABASE_URL=postgresql://user:pass@host:5432/todoapp

# Auth (existing from Phase II)
JWT_SECRET=your-secret-key
```

**Security Note**: NEVER commit `.env` file to version control

---

## Step 2: Database Migration

### 2.1 Create Migration File

```bash
cd backend/migrations

# Create new migration file
touch 001_add_chat_tables.sql
```

### 2.2 Run Migration Script

Copy the migration SQL from `data-model.md` and execute:

```bash
# Using psql
psql $DATABASE_URL -f migrations/001_add_chat_tables.sql

# Or using SQLModel/Alembic (if configured)
alembic upgrade head
```

### 2.3 Verify Tables Created

```bash
psql $DATABASE_URL -c "\dt"  # List tables

# Should see:
# - conversations
# - messages
# - tasks (existing)
# - users (existing)
```

---

## Step 3: Implement MCP Server

### 3.1 Create MCP Server Module

```bash
cd backend
mkdir -p mcp/tools

# Create files
touch mcp/__init__.py
touch mcp/server.py
touch mcp/tools/__init__.py
touch mcp/tools/add_task.py
touch mcp/tools/list_tasks.py
touch mcp/tools/complete_task.py
touch mcp/tools/delete_task.py
touch mcp/tools/update_task.py
```

### 3.2 Implement MCP Tools

Use the tool schemas from `contracts/mcp-tools.json` as reference.

**Example: `mcp/tools/add_task.py`**
```python
from sqlmodel import Session
from backend.models import Task
from datetime import datetime

async def add_task(user_id: str, title: str, description: str = None):
    """MCP tool: Create a new task"""

    # Validate title length
    if not title or len(title) > 200:
        raise ValueError("Title must be 1-200 characters")

    # Create task
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )

    # Save to database (use dependency injection in actual impl)
    # session.add(task)
    # session.commit()
    # session.refresh(task)

    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }
```

### 3.3 Register MCP Server

**File: `mcp/server.py`**
```python
from mcp.server import Server
from mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task
)

mcp_server = Server("todo-mcp-server")

# Register tools
mcp_server.tool()(add_task)
mcp_server.tool()(list_tasks)
mcp_server.tool()(complete_task)
mcp_server.tool()(delete_task)
mcp_server.tool()(update_task)

def get_mcp_server():
    return mcp_server
```

---

## Step 4: Implement Chat API Endpoint

### 4.1 Create Database Models

**File: `backend/models/conversation.py`**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4.2 Create Chat Service

**File: `backend/services/chat_service.py`**
```python
from openai import Client
from backend.mcp.server import get_mcp_server
import os

openai_client = Client(api_key=os.getenv("OPENAI_API_KEY"))
mcp_server = get_mcp_server()

async def process_chat_message(
    user_id: str,
    conversation_id: int | None,
    message: str
):
    # 1. Load or create conversation
    # 2. Load last 50 messages for context
    # 3. Build message array
    # 4. Execute OpenAI agent with MCP tools
    # 5. Store user and assistant messages
    # 6. Return response

    pass  # Implementation follows spec requirements
```

### 4.3 Create API Route

**File: `backend/routes/chat.py`**
```python
from fastapi import APIRouter, Depends, HTTPException
from backend.auth import get_current_user
from backend.services.chat_service import process_chat_message
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: int | None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list[dict]

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # Validate user_id matches authenticated user
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Process chat message
    response = await process_chat_message(
        user_id=user_id,
        conversation_id=request.conversation_id,
        message=request.message
    )

    return response
```

---

## Step 5: Implement Frontend Chat UI

### 5.1 Create Chat Page

**File: `frontend/src/app/chat/page.tsx`**
```typescript
'use client';

import { ChatWindow } from '@openai/chatkit';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function ChatPage() {
  const { user, token } = useAuth();
  const [conversationId, setConversationId] = useState<number | null>(null);

  async function handleMessage(message: string) {
    const response = await fetch(`/api/${user.id}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message
      })
    });

    const data = await response.json();

    // Update conversation ID if new conversation created
    if (!conversationId) {
      setConversationId(data.conversation_id);
    }

    return data.response;
  }

  return (
    <div className="h-screen">
      <ChatWindow
        onMessage={handleMessage}
        placeholder="Ask me to manage your tasks..."
        className="w-full h-full"
      />
    </div>
  );
}
```

### 5.2 Add Navigation Link

Update your navigation to include link to `/chat` page.

---

## Step 6: Testing

### 6.1 Unit Tests

```bash
# Test MCP tools
pytest backend/tests/mcp/test_add_task.py
pytest backend/tests/mcp/test_list_tasks.py

# Test chat endpoint
pytest backend/tests/routes/test_chat.py
```

### 6.2 Integration Tests

```bash
# Test full chat flow
pytest backend/tests/integration/test_chat_flow.py
```

### 6.3 Manual Testing

```bash
# Start backend
cd backend
uvicorn main:app --reload

# Start frontend (separate terminal)
cd frontend
npm run dev

# Open browser
open http://localhost:3000/chat
```

**Test Scenarios:**
1. Send message: "I need to buy groceries"
2. Verify task created: "Show my tasks"
3. Complete task: "Mark groceries as done"
4. Delete task: "Delete the groceries task"

---

## Step 7: Deployment

### 7.1 Backend Deployment

```bash
# Ensure environment variables set in production
# Deploy to existing backend infrastructure (same as Phase II)
```

### 7.2 Frontend Deployment

```bash
cd frontend

# Build production bundle
npm run build

# Deploy to Vercel or existing hosting
vercel deploy --prod
```

### 7.3 Database Migration (Production)

```bash
# Run migration on production database
psql $PRODUCTION_DATABASE_URL -f migrations/001_add_chat_tables.sql
```

---

## Step 8: Monitoring & Observability

### 8.1 Configure Structured Logging

Ensure `structlog` is configured with JSON formatter and correlation IDs.

### 8.2 Add Health Check Endpoint

```python
@router.get("/health/mcp")
async def mcp_health_check():
    return {
        "status": "healthy",
        "mcp_server": "running",
        "tools": len(mcp_server.get_tools())
    }
```

### 8.3 Monitor Key Metrics

- Chat response time (target: <3s p95)
- OpenAI API error rate
- Database query performance
- MCP tool execution time

---

## Common Issues & Troubleshooting

### Issue: OpenAI API Rate Limit

**Symptoms**: 429 errors, requests failing
**Solution**: Implement exponential backoff (see `research.md` Section 5)

### Issue: Slow Chat Response

**Symptoms**: >3s response time
**Solution**: Check database query performance, add indexes, optimize message loading

### Issue: Conversation Not Loading

**Symptoms**: 404 error when opening conversation
**Solution**: Verify conversation ownership, check user_id matches JWT token

### Issue: MCP Tools Not Registering

**Symptoms**: Agent doesn't use tools, returns generic responses
**Solution**: Verify MCP server initialized before agent, check tool schemas match

---

## Next Steps

After completing quickstart:

1. Run `/sp.tasks` to generate implementation task breakdown
2. Follow red-green-refactor cycle for TDD implementation
3. Review generated code against spec acceptance criteria
4. Update constitution if architectural decisions change

---

## Reference Documents

- [Specification](./spec.md) - Requirements and acceptance criteria
- [Plan](./plan.md) - Architectural decisions and structure
- [Research](./research.md) - Technology choices and patterns
- [Data Model](./data-model.md) - Database schema and entities
- [API Contract](./contracts/chat-api.yaml) - REST API specification
- [MCP Tools Contract](./contracts/mcp-tools.json) - MCP tool schemas

---

## Support

For questions or issues:
- Review spec.md for requirements clarification
- Check research.md for technology patterns
- Consult CLAUDE.md for implementation guidance
- Create GitHub issue if blocked
