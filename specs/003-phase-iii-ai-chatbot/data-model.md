# Data Model: Phase III - Todo AI Chatbot

**Feature**: Phase III - Todo AI Chatbot
**Date**: 2025-12-31
**Status**: Phase 1 Complete

## Overview

This document defines the data entities, relationships, validation rules, and lifecycle management for the AI chatbot feature. The model extends the existing Phase II schema with conversation and message entities while reusing the tasks table unchanged.

---

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │ (existing from Phase II)
│─────────────│
│ id (PK)     │
│ email       │
│ name        │
└──────┬──────┘
       │ 1
       │
       │ *
┌──────┴────────────┐
│   Conversation    │
│───────────────────│
│ id (PK)           │
│ user_id (FK)      │
│ created_at        │
│ updated_at        │
└──────┬────────────┘
       │ 1
       │
       │ *
┌──────┴────────────┐
│     Message       │
│───────────────────│
│ id (PK)           │
│ conversation_id(FK)│
│ user_id (FK)      │
│ role              │
│ content           │
│ created_at        │
└───────────────────┘

       User ──────┐ 1
                  │
                  │ *
       ┌──────────┴────┐
       │     Task      │ (existing from Phase II, unchanged)
       │───────────────│
       │ id (PK)       │
       │ user_id (FK)  │
       │ title         │
       │ description   │
       │ completed     │
       │ created_at    │
       │ updated_at    │
       └───────────────┘
```

---

## Entities

### 1. Conversation

**Purpose**: Represents a chat session between a user and the AI assistant

**Table**: `conversations`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing conversation ID |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | Owner of the conversation |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Conversation creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

#### Indexes

```sql
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);  -- For sorting by recency
```

#### Validation Rules

- `user_id` MUST reference existing user in users table
- `created_at` MUST be ≤ `updated_at`
- Cannot be created without associated user

#### Lifecycle

1. **Creation**: Auto-created when user sends first message without conversation_id
2. **Updates**: `updated_at` timestamp refreshed on every new message
3. **Retention**:
   - Active: 90 days from last update
   - Archived: 1 year after becoming inactive
   - Deletion: Permanent removal after archive period
4. **Cascade**: Messages deleted when conversation deleted (ON DELETE CASCADE)

#### State Transitions

```
[New] → [Active] → [Inactive (90d)] → [Archived (1y)] → [Deleted]
          ↑──────────┘
     (new message reactivates)
```

#### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def touch(self):
        """Update timestamp when new message added"""
        self.updated_at = datetime.utcnow()
```

---

### 2. Message

**Purpose**: Individual user or assistant message within a conversation

**Table**: `messages`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing message ID |
| conversation_id | INTEGER | NOT NULL, FOREIGN KEY → conversations(id) ON DELETE CASCADE | Parent conversation |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | User who owns this conversation |
| role | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant')) | Message sender role |
| content | TEXT | NOT NULL | Message text content |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message creation timestamp |

#### Indexes

```sql
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(conversation_id, created_at);  -- For pagination
```

#### Validation Rules

- `conversation_id` MUST reference existing conversation
- `user_id` MUST match conversation owner
- `role` MUST be either 'user' or 'assistant'
- `content` MUST NOT be empty (minimum 1 character)
- `content` MUST be ≤ 1000 characters for user messages
- Messages are immutable after creation (no UPDATE operations)

#### Lifecycle

1. **Creation**: Created when user sends message or agent responds
2. **Immutability**: Never modified after insertion
3. **Retention**: Same as parent conversation (90 days active + 1 year archive)
4. **Deletion**: Cascade deleted with conversation

#### Loading Strategy

- **Display**: Load last 50 messages per conversation by default
- **AI Context**: Send last 50 messages to OpenAI agent
- **Pagination**: Load older messages in batches of 50 on scroll
- **Query**: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 50`

#### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: MessageRole
    content: str = Field(max_length=10000)  # Allow longer assistant responses
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __init__(self, **data):
        super().__init__(**data)
        if self.role == MessageRole.USER and len(self.content) > 1000:
            raise ValueError("User messages limited to 1000 characters")
```

---

### 3. Task (Existing - No Schema Changes)

**Purpose**: Todo task item manageable via chat MCP tools

**Table**: `tasks` (from Phase II - unchanged)

#### Fields (Reference Only)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Task ID |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users(id) | Task owner |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULL | Optional task description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification timestamp |

#### MCP Tool Operations

Tasks are accessed via MCP tools only (not directly from chat endpoint):

1. **add_task**: INSERT new task
2. **list_tasks**: SELECT with optional status filter
3. **complete_task**: UPDATE completed = TRUE
4. **delete_task**: DELETE task
5. **update_task**: UPDATE title or description

#### Validation in MCP Tools

- `title`: 1-200 characters (enforced in add_task and update_task)
- `description`: ≤ 1000 characters if provided
- `user_id`: Must match authenticated user from JWT token
- Task ownership validated before any modification

---

## Relationships

### User → Conversation (1:Many)

- One user can have multiple conversations
- Conversation always belongs to exactly one user
- Foreign key: `conversations.user_id → users.id`
- Cascade: Delete conversations when user deleted (implementation detail)

### Conversation → Message (1:Many)

- One conversation contains multiple messages
- Message always belongs to exactly one conversation
- Foreign key: `messages.conversation_id → conversations.id`
- Cascade: **ON DELETE CASCADE** (messages deleted with conversation)

### User → Message (1:Many)

- One user owns multiple messages
- Message owner always matches conversation owner
- Foreign key: `messages.user_id → users.id`
- Purpose: Direct query path for user's messages without JOIN

### User → Task (1:Many)

- One user owns multiple tasks
- Task always belongs to exactly one user
- Foreign key: `tasks.user_id → users.id`
- **No relationship to Conversation/Message**: Tasks accessed via MCP tools

---

## Database Migration

### Migration Script: `001_add_chat_tables.sql`

```sql
-- Add conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);

-- Add messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(conversation_id, created_at);

-- Add trigger to update conversation.updated_at on new message
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NEW.created_at
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
```

### Rollback Script: `001_add_chat_tables_rollback.sql`

```sql
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;
DROP FUNCTION IF EXISTS update_conversation_timestamp();
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
```

---

## Data Lifecycle Management

### Conversation Archival Process

**Schedule**: Daily cron job at 2:00 AM UTC

```sql
-- Mark conversations inactive after 90 days
UPDATE conversations
SET status = 'inactive'
WHERE updated_at < NOW() - INTERVAL '90 days'
AND status = 'active';

-- Archive conversations inactive for 1 year
INSERT INTO conversations_archive
SELECT * FROM conversations
WHERE updated_at < NOW() - INTERVAL '1 year' - INTERVAL '90 days'
AND status = 'inactive';

-- Delete archived conversations (CASCADE deletes messages)
DELETE FROM conversations
WHERE id IN (
    SELECT id FROM conversations_archive
);
```

**Note**: Add `status` column in future enhancement if explicit archival tracking needed

---

## Query Patterns

### Common Queries

**1. Load conversation list for user:**
```sql
SELECT id, created_at, updated_at
FROM conversations
WHERE user_id = ?
ORDER BY updated_at DESC
LIMIT 20;
```

**2. Load recent messages in conversation:**
```sql
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 50;
```

**3. Search conversations by content:**
```sql
SELECT DISTINCT c.id, c.updated_at
FROM conversations c
JOIN messages m ON m.conversation_id = c.id
WHERE c.user_id = ?
AND m.content ILIKE ?
ORDER BY c.updated_at DESC;
```

**4. Create new conversation with first message:**
```sql
BEGIN;
INSERT INTO conversations (user_id) VALUES (?) RETURNING id;
INSERT INTO messages (conversation_id, user_id, role, content) VALUES (?, ?, 'user', ?);
COMMIT;
```

### Performance Considerations

- Use prepared statements for all queries
- Connection pooling (10-20 connections recommended)
- Query timeout: 5 seconds
- Enable query logging for slow queries (>500ms)

---

## Summary

**New Tables**: 2 (conversations, messages)
**Modified Tables**: 0 (tasks table unchanged)
**Indexes Added**: 6 total
**Foreign Key Constraints**: 4 total
**Triggers**: 1 (auto-update conversation timestamp)

**Compliance**:
- ✅ Stateless architecture (no in-memory state)
- ✅ Data isolation (user_id on all tables)
- ✅ Referential integrity (CASCADE deletes)
- ✅ Performance indexes (user_id, timestamps)
- ✅ Retention policy (90 days + 1 year archive)
