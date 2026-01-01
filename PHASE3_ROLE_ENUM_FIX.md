# Phase III - Message Role Enum Fix

## Issue: Database Constraint Violation

### Problem
When sending chat messages, the backend was throwing a PostgreSQL check constraint error:
```
psycopg2.errors.CheckViolation: new row for relation "messages" violates check constraint "messages_role_check"
DETAIL: Failing row contains (1, 1, user_556b58c8012446c5, USER, hi, ...).
```

The database constraint expected lowercase values (`'user'`, `'assistant'`), but SQLAlchemy/SQLModel was trying to insert the enum **name** (`USER`, `ASSISTANT`) instead of the enum **value** (`"user"`, `"assistant"`).

### Root Cause
The `Message` model had a field defined as:
```python
role: MessageRole  # Enum type
```

When SQLModel tried to serialize this to the database, it was using the enum name (uppercase) instead of the enum value (lowercase), causing a constraint violation.

### Solution

#### 1. Changed Message Model Field Type
**File:** `backend/models/conversation.py`

Changed the `role` field from enum type to string type:
```python
# Before
role: MessageRole

# After
role: str = Field(sa_column_kwargs={"nullable": False})
```

Added validation in the `__init__` method:
```python
def __init__(self, **data):
    """Validate user message length and role on initialization"""
    super().__init__(**data)

    # Validate role
    if self.role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
        raise ValueError(f"Invalid role: {self.role}. Must be 'user' or 'assistant'")

    # Validate user message length
    if self.role == MessageRole.USER.value and len(self.content) > 1000:
        raise ValueError("User messages limited to 1000 characters")
```

#### 2. Updated save_message Calls
**File:** `backend/services/chat_service.py`

Changed all calls to `save_message` to pass the enum **value** instead of the enum itself:

```python
# User message (line 203)
self.save_message(
    conversation_id=conversation.id,
    user_id=user_id,
    role=MessageRole.USER.value,  # Was: MessageRole.USER
    content=request.message
)

# Assistant message (line 271)
self.save_message(
    conversation_id=conversation.id,
    user_id=user_id,
    role=MessageRole.ASSISTANT.value,  # Was: MessageRole.ASSISTANT
    content=assistant_content
)
```

#### 3. Updated save_message Method Signature
**File:** `backend/services/chat_service.py` (line 115-136)

Changed the parameter type from `MessageRole` to `str` and added validation:

```python
def save_message(
    self,
    conversation_id: int,
    user_id: str,
    role: str,  # Changed from MessageRole
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

    # ... rest of method
```

## Files Modified

1. `backend/models/conversation.py`
   - Changed `role` field type from `MessageRole` to `str`
   - Enhanced `__init__` validation for role values

2. `backend/services/chat_service.py`
   - Updated `save_message` method signature (line 115-136)
   - Changed user message save call to use `.value` (line 203)
   - Changed assistant message save call to use `.value` (line 271)

## Testing

### Manual Test
1. Start the backend server
2. Navigate to the chat page
3. Send a message like "hi"
4. Verify the message is saved successfully
5. Check that the assistant responds

### Database Verification
Run this query to verify messages are being stored with correct role values:
```sql
SELECT id, role, content, created_at
FROM messages
ORDER BY created_at DESC
LIMIT 10;
```

Expected output:
- `role` column should contain lowercase values: `'user'` or `'assistant'`
- No constraint violations

### Python Verification
```python
from models.conversation import MessageRole

# Verify enum values are lowercase
assert MessageRole.USER.value == "user"
assert MessageRole.ASSISTANT.value == "assistant"
```

## Important Notes

### MessageRole Enum Still Used
The `MessageRole` enum is still defined and used throughout the codebase for:
- Type safety in function signatures
- Constants for role values
- Validation logic

The key change is that we now explicitly use `.value` when passing to the database layer.

### Database Schema
The database check constraint remains unchanged:
```sql
CHECK (((role)::text = ANY ((ARRAY['user'::character varying, 'assistant'::character varying])::text[])))
```

This constraint is correct and will now work properly with the fixed code.

## Security Note

⚠️ **CRITICAL:** An OpenAI API key was exposed in the error logs. If this happened:
1. Immediately revoke the exposed key at https://platform.openai.com/api-keys
2. Generate a new API key
3. Update the `.env` file with the new key
4. Never commit API keys to version control
5. Add `.env` to `.gitignore` if not already there

---

**Status:** Fixed ✅
**Date:** 2026-01-01
**Phase:** Phase III - AI Chatbot Integration
