# Phase 0: Research & Technology Decisions

**Feature**: Phase III - Todo AI Chatbot
**Date**: 2025-12-31
**Status**: Complete

## Overview

This document captures research findings and technology decisions for implementing an AI-powered chat interface for todo task management using Model Context Protocol (MCP) architecture.

---

## 1. MCP Server Implementation

### Decision
Use **Official MCP Python SDK** (`mcp` package) for MCP server implementation

### Rationale
- Official SDK maintained by Anthropic/MCP community
- Native Python integration with FastAPI backend
- Provides standard tool registration decorator pattern
- Built-in JSON schema validation for tool parameters
- Supports both stdio and HTTP transport modes

### Alternatives Considered
- **Custom MCP implementation**: Rejected due to protocol complexity and maintenance burden
- **Third-party MCP libraries**: Rejected due to lack of official support and uncertain maintenance

### Implementation Pattern
```python
from mcp.server import Server

mcp_server = Server("todo-mcp-server")

@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str = None):
    """MCP tool for creating tasks"""
    # Tool implementation with SQLModel database access
    pass
```

### Best Practices
- One tool per task operation (add, list, complete, delete, update)
- All tools validate user_id for authorization
- Return structured JSON responses with status codes
- Log all tool invocations with correlation IDs

---

## 2. OpenAI Agents SDK Integration

### Decision
Use **OpenAI Agents SDK** (official OpenAI library) with gpt-4o-mini model

### Rationale
- Official SDK with stable API and ongoing support
- Built-in MCP tool registration support
- Handles context management and conversation history
- Supports streaming responses for better UX
- Cost-effective with gpt-4o-mini ($0.15/1M input tokens, $0.60/1M output tokens)

### Alternatives Considered
- **LangChain**: Rejected due to added abstraction layer complexity
- **Direct OpenAI API**: Rejected due to lack of agent-level abstractions
- **Anthropic Claude**: Rejected to stay within OpenAI ecosystem per spec requirement

### Agent Configuration Pattern
```python
from openai import Client
from openai.agents import Agent

client = Client(api_key=os.getenv("OPENAI_API_KEY"))

agent = Agent(
    model="gpt-4o-mini",
    instructions=TASK_MANAGEMENT_INSTRUCTIONS,
    tools=[mcp_server.get_tools()],  # Register MCP tools
    temperature=0.7
)
```

### Best Practices
- System instructions define task management intent patterns
- Temperature 0.7 balances creativity and consistency
- Tool choice mode: "auto" (agent decides when to use tools)
- Context window: 128k tokens (sufficient for 50 message history)

---

## 3. Chat Interface: OpenAI ChatKit

### Decision
Use **OpenAI ChatKit** React component library

### Rationale
- Official OpenAI UI component designed for chat interfaces
- Handles message display, input, and loading states
- Built-in support for streaming responses
- Customizable styling with Tailwind CSS
- TypeScript-first with strong typing

### Alternatives Considered
- **Custom React chat UI**: Rejected due to development time and maintenance
- **Vercel AI SDK Chat**: Rejected to stay within OpenAI ecosystem
- **react-chatbot-kit**: Rejected due to lack of OpenAI-specific features

### Implementation Pattern
```typescript
import { ChatWindow } from '@openai/chatkit';

export default function ChatPage() {
  return (
    <ChatWindow
      apiEndpoint="/api/{user_id}/chat"
      conversationId={conversationId}
      onMessage={handleMessage}
      authToken={jwtToken}
    />
  );
}
```

### Best Practices
- Server-side JWT validation on API endpoint
- Optimistic UI updates for better perceived performance
- Error boundary for graceful failure handling
- Retry mechanism for transient network failures

---

## 4. Conversation State Management

### Decision
**Database-backed stateless architecture** with PostgreSQL for conversation/message persistence

### Rationale
- Aligns with Constitution Principle III (Stateless Architecture)
- Enables horizontal scaling without state synchronization
- Survives server restarts (no data loss)
- Allows conversation history replay for context
- Existing Neon PostgreSQL database can be extended

### Alternatives Considered
- **Redis for session state**: Rejected as violates stateless principle (state in memory)
- **LocalStorage only**: Rejected due to security concerns and lack of cross-device sync
- **Serverless KV store**: Rejected to minimize external dependencies

### Database Schema
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

### Best Practices
- Pagination: Load last 50 messages per conversation
- Soft delete with archival after 90 days
- Indexes on user_id and conversation_id for query performance
- CASCADE delete for referential integrity

---

## 5. Rate Limiting & Queueing Strategy

### Decision
**Request queue with exponential backoff** for OpenAI API rate limit handling

### Rationale
- Recommended approach by OpenAI documentation
- Prevents request loss during rate limit events
- Graceful degradation vs. immediate failure
- Maintains request order (FIFO queue)
- User notification for transparency

### Alternatives Considered
- **Immediate failure**: Rejected due to poor UX
- **Silent retry without queue**: Rejected due to potential request duplication
- **Client-side retry**: Rejected to keep complexity on server

### Implementation Pattern
```python
from asyncio import Queue, sleep

request_queue = Queue()

async def process_with_backoff(request):
    retries = 0
    max_retries = 5
    base_delay = 1  # seconds

    while retries < max_retries:
        try:
            response = await openai_agent.run(request)
            return response
        except RateLimitError as e:
            delay = base_delay * (2 ** retries)  # Exponential backoff
            await sleep(delay)
            retries += 1

    raise Exception("Max retries exceeded")
```

### Best Practices
- Max 5 retries with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Queue depth monitoring with alerts
- User notification after first retry: "Processing your request..."
- Timeout after 30 seconds total wait time

---

## 6. Observability & Monitoring

### Decision
**Structured JSON logging with correlation IDs** and OpenTelemetry metrics

### Rationale
- Industry-standard approach for distributed systems
- Enables end-to-end request tracing
- Integrates with log aggregation tools (CloudWatch, Datadog)
- Low overhead with sampling (1% success rate, 100% errors)
- Supports debugging and performance analysis

### Alternatives Considered
- **Plain text logs**: Rejected due to lack of structured querying
- **No sampling**: Rejected due to log volume concerns
- **Metrics only**: Rejected due to lack of debug context

### Logging Pattern
```python
import structlog
import uuid

logger = structlog.get_logger()

@app.post("/api/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest):
    correlation_id = str(uuid.uuid4())

    logger.info("chat_request_received",
        correlation_id=correlation_id,
        user_id=user_id,
        conversation_id=request.conversation_id,
        message_length=len(request.message)
    )

    try:
        response = await process_chat(request)
        logger.info("chat_request_success",
            correlation_id=correlation_id,
            response_time_ms=elapsed
        )
        return response
    except Exception as e:
        logger.error("chat_request_failed",
            correlation_id=correlation_id,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise
```

### Metrics to Track
- `chat.response_time` (histogram)
- `chat.error_rate` (counter)
- `mcp.tool_execution_time` (histogram)
- `openai.api_calls` (counter)
- `queue.depth` (gauge)

### Best Practices
- Correlation ID passed to all downstream operations
- No sensitive data in logs (PII, message content, API keys)
- Structured log format for machine parsing
- Sample successful requests at 1%, log all errors

---

## 7. Security & Authentication

### Decision
**Reuse existing Better Auth JWT implementation** with endpoint-level validation

### Rationale
- Already implemented in Phase II
- JWT tokens provide stateless auth (no session store needed)
- Integrates with FastAPI dependency injection
- User ID embedded in token for authorization

### Authorization Pattern
```python
from fastapi import Depends, HTTPException
from backend.auth import get_current_user

@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # Validate user_id in URL matches authenticated user
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Proceed with chat processing
    ...
```

### Security Best Practices
- JWT validation on every request (no caching)
- user_id parameter validation against token
- Conversation ownership check before access
- Task ownership validation in MCP tools
- OpenAI API key in environment variables only
- HTTPS for all API communication

---

## 8. Testing Strategy

### Decision
**Layered testing approach**: Unit tests, integration tests, contract tests

### Rationale
- Unit tests for business logic and MCP tools
- Integration tests for API endpoints and database
- Contract tests for MCP tool schemas and API responses
- Matches existing Phase II testing patterns

### Testing Stack
- **Backend**: pytest, pytest-asyncio, pytest-cov
- **Frontend**: Jest, React Testing Library, MSW (Mock Service Worker)
- **E2E**: Playwright (optional for critical flows)

### Test Coverage Goals
- Unit tests: 80% coverage minimum
- Integration tests: All API endpoints
- Contract tests: All MCP tools and API responses

---

## 9. Deployment Strategy

### Decision
**Extend existing deployment**: Backend on same server, Frontend in Next.js app

### Rationale
- Minimal infrastructure changes
- Reuse existing database connection
- Leverage Phase II deployment pipeline
- MCP server runs as part of FastAPI process

### Deployment Architecture
```
Frontend (Next.js/Vercel)
    ↓ HTTPS
Backend (FastAPI)
    ├── Chat API Endpoint
    ├── MCP Server (port 3001)
    └── Task API Endpoints (existing)
    ↓
Database (Neon PostgreSQL)
    ├── users (existing)
    ├── tasks (existing)
    ├── conversations (new)
    └── messages (new)
```

### Best Practices
- Environment variables for API keys (OPENAI_API_KEY)
- Database migrations for new tables
- Health check endpoint for MCP server
- Graceful shutdown handling for in-flight requests

---

## 10. Performance Optimizations

### Decisions

**Database Query Optimization:**
- Indexes on user_id, conversation_id for fast lookups
- LIMIT 50 for message pagination
- Connection pooling (10-20 connections)

**API Response Optimization:**
- Stream chat responses for better perceived performance
- Cache conversation list with 1-minute TTL
- Batch database writes where possible

**Frontend Optimization:**
- Code splitting for ChatKit component
- Virtual scrolling for long conversation lists
- Optimistic UI updates for instant feedback

### Performance Targets (from spec)
- Chat endpoint: <3s response time (95th percentile) ✓
- Database queries: <500ms ✓
- MCP tool execution: <1s ✓
- Support 100 concurrent users ✓

---

## Summary

All technology decisions align with:
- ✅ Constitution principles (stateless, MCP-first, spec-driven)
- ✅ Performance requirements (<3s response, 100 concurrent users)
- ✅ Security constraints (JWT auth, data isolation)
- ✅ Scalability goals (horizontal scaling, 10k+ conversations)
- ✅ Existing Phase II architecture (FastAPI + Next.js + PostgreSQL)

**No unresolved "NEEDS CLARIFICATION" items remain.**

**Next Phase**: Phase 1 - Design data model, generate API contracts, create quickstart guide
