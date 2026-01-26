# Data Model: Advanced Todo Features

## Core Entities

### Task
- `id`: integer (primary key, auto-increment)
- `user_id`: string (foreign key to User)
- `title`: string (not null, max 500 chars)
- `description`: text (nullable)
- `completed`: boolean (default false)
- `priority`: string enum ('low', 'medium', 'high', 'urgent') (default 'medium')
- `tags`: array of strings (nullable)
- `category`: string (nullable, max 100 chars)
- `due_date`: timestamp (nullable)
- `reminder_settings`: JSON object (nullable)
- `reminder_sent`: boolean (default false)
- `created_at`: timestamp (default now)
- `updated_at`: timestamp (default now)
- `completed_at`: timestamp (nullable)

### RecurringTask (extends Task)
- `is_recurring`: boolean (default false)
- `recurrence_pattern`: JSONB object (not null)
- `parent_task_id`: integer (foreign key to Task, nullable)
- `next_occurrence_date`: timestamp (nullable)

### RecurrencePattern
- `type`: string enum ('daily', 'weekly', 'monthly', 'custom')
- `interval`: integer (e.g., every N days/weeks/months)
- `days_of_week`: array of integers (0-6 for Sunday-Saturday, nullable)
- `day_of_month`: integer (1-31, nullable)
- `end_condition`: JSON object with:
  - `type`: string enum ('never', 'after_n_occurrences', 'by_date')
  - `value`: integer or datetime (nullable)

### User
- `id`: string (primary key)
- `timezone`: string (default 'UTC')
- `created_at`: timestamp (default now)
- `updated_at`: timestamp (default now)

### Reminder
- `id`: integer (primary key, auto-increment)
- `task_id`: integer (foreign key to Task)
- `user_id`: string (foreign key to User)
- `scheduled_for`: timestamp (not null)
- `status`: string enum ('pending', 'sent', 'cancelled') (default 'pending')
- `created_at`: timestamp (default now)

### Tag
- `id`: integer (primary key, auto-increment)
- `name`: string (unique, not null)
- `user_id`: string (foreign key to User, nullable for global tags)
- `created_at`: timestamp (default now)

## Relationships

- User (1) -> Task (Many): A user can have many tasks
- Task (1) -> RecurringTask (1): A task can be a recurring task
- Task (1) -> Reminder (Many): A task can have many reminder schedules
- Task (Many) -> Tag (Many): Tasks can have multiple tags and tags can be on multiple tasks
- User (1) -> Tag (Many): A user can create personal tags

## Validation Rules

### Task Validation
- Title is required and must be between 1-500 characters
- Priority must be one of 'low', 'medium', 'high', 'urgent'
- Due date cannot be in the past if creating new task
- Completed tasks cannot have due dates in the future (optional business rule)

### RecurringTask Validation
- If `is_recurring` is true, `recurrence_pattern` must be provided
- `recurrence_pattern.type` must be one of 'daily', 'weekly', 'monthly', 'custom'
- If `type` is 'weekly', `days_of_week` must be provided and contain valid day numbers (0-6)
- If `type` is 'monthly', either `day_of_month` or `days_of_week` must be provided
- `interval` must be a positive integer

### User Validation
- `timezone` must be a valid IANA timezone identifier
- `user_id` must be unique

### Reminder Validation
- `scheduled_for` must be in the future
- `status` must be one of 'pending', 'sent', 'cancelled'

## State Transitions

### Task States
- `created` → `in_progress` → `completed` (optional intermediate state)
- `created` → `completed`
- `completed` → `reopened` (for non-recurring tasks)

### RecurringTask States
- `created` → `scheduled_next_occurrence` → `completed` → `next_created`
- When completed, system automatically creates the next occurrence based on the recurrence pattern

### Reminder States
- `created` → `pending` → `sent`/`cancelled`
- `pending` → `rescheduled` (if user snoozes the reminder)