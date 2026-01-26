-- Migration: Extend task table with new columns for advanced features
-- Description: Add priority, tags, due_date, recurrence, and reminder fields to tasks table

-- Add new columns to tasks table
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium',
ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS due_date TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS recurrence_settings JSONB,
ADD COLUMN IF NOT EXISTS reminder_settings JSONB;

-- Add validation constraints
DO $$
BEGIN
    -- Create enum type for priority if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'priority_enum') THEN
        CREATE TYPE priority_enum AS ENUM ('high', 'medium', 'low');
    END IF;
END$$;

-- Update the priority column to use the enum type
-- First drop the existing column and recreate with enum type
-- ALTER TABLE tasks DROP COLUMN priority;
-- ALTER TABLE tasks ADD COLUMN priority priority_enum DEFAULT 'medium';

-- Add constraint for priority values (alternative approach if enum creation is restricted)
ALTER TABLE tasks
ADD CONSTRAINT chk_priority CHECK (
    priority IN ('high', 'medium', 'low')
);

-- Add constraint for tags array length
ALTER TABLE tasks
ADD CONSTRAINT chk_tags_length CHECK (
    jsonb_array_length(tags) <= 10
);

-- Add constraint for due_date to be in the future if specified
ALTER TABLE tasks
ADD CONSTRAINT chk_due_date_future CHECK (
    due_date IS NULL OR due_date > NOW()
);

-- Add constraint for recurrence settings when is_recurring is true
ALTER TABLE tasks
ADD CONSTRAINT chk_recurrence_settings CHECK (
    (is_recurring = FALSE) OR (is_recurring = TRUE AND recurrence_settings IS NOT NULL)
);

-- Add constraint for reminder offset to be positive if settings exist
ALTER TABLE tasks
ADD CONSTRAINT chk_reminder_offset CHECK (
    (reminder_settings IS NULL) OR (reminder_settings->>'offset_minutes' IS NULL) OR ((reminder_settings->>'offset_minutes')::INTEGER >= 0)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- Create GIN index for tags for efficient JSONB querying
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN(tags);

-- Insert sample data for testing if table is empty
DO $$
DECLARE
    row_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO row_count FROM tasks;

    IF row_count = 0 THEN
        INSERT INTO tasks (title, description, status, priority, tags, due_date, is_recurring, user_id, created_at, updated_at) VALUES
        ('Sample Task with Priority', 'This is a sample task with high priority', 'pending', 'high', '["work", "important"]', NOW() + INTERVAL '1 day', FALSE, 'user123', NOW(), NOW()),
        ('Recurring Task Sample', 'This task recurs weekly', 'pending', 'medium', '["recurring", "routine"]', NOW() + INTERVAL '2 days', TRUE, 'user123', NOW(), NOW()),
        ('Task with Due Date', 'This task has a due date', 'pending', 'low', '["personal"]', NOW() + INTERVAL '7 days', FALSE, 'user123', NOW(), NOW());
    END IF;
END$$;

COMMIT;