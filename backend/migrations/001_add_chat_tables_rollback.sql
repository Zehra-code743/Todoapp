-- Rollback: Remove conversations and messages tables
-- Author: Phase III Implementation
-- Date: 2026-01-01

DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;
DROP FUNCTION IF EXISTS update_conversation_timestamp();
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
