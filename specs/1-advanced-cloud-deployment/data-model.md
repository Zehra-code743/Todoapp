# Data Model: Advanced Cloud Deployment with Event-Driven Architecture

## Task Entity

### Fields
- **id** (INTEGER, PRIMARY KEY, AUTO_INCREMENT) - Unique identifier for the task
- **title** (VARCHAR(255), NOT NULL) - Title of the task
- **description** (TEXT, NULL) - Optional detailed description of the task
- **status** (VARCHAR(20), DEFAULT 'pending') - Status of the task ('pending', 'completed')
- **priority** (VARCHAR(10), DEFAULT 'medium') - Priority level ('high', 'medium', 'low')
- **tags** (JSONB, DEFAULT '[]'::jsonb) - Array of tag strings for categorization
- **due_date** (TIMESTAMPTZ, NULL) - Date and time when the task is due
- **is_recurring** (BOOLEAN, DEFAULT FALSE) - Whether this task is recurring
- **recurrence_settings** (JSONB, NULL) - Configuration for recurrence patterns
  - pattern (ENUM: 'daily', 'weekly', 'monthly', 'yearly')
  - interval (INTEGER) - How often to repeat (every N days/weeks/months/years)
  - days (ARRAY) - Days of week for weekly recurrence (e.g., ['Mon', 'Wed', 'Fri'])
  - end_date (DATE, NULL) - When to stop recurrence
- **reminder_settings** (JSONB, NULL) - Configuration for reminder notifications
  - offset_minutes (INTEGER) - Minutes before due time to send reminder
  - channel (ENUM: 'in_app', 'email', 'push', 'sms') - Notification channel
- **user_id** (VARCHAR(255), NOT NULL) - Identifier of the user who owns the task
- **created_at** (TIMESTAMPTZ, DEFAULT NOW()) - Timestamp when task was created
- **updated_at** (TIMESTAMPTZ, DEFAULT NOW()) - Timestamp when task was last updated
- **completed_at** (TIMESTAMPTZ, NULL) - Timestamp when task was marked as completed

### Validation Rules
- Title must be between 1-255 characters
- Priority must be one of 'high', 'medium', 'low'
- Tags array must not exceed 10 tags per task
- Due date must be in the future if specified
- Recurrence settings required if is_recurring is TRUE
- Reminder offset must be positive if reminder settings are configured

### State Transitions
- pending → completed (when task is marked as done)
- completed → (new recurring instance created if is_recurring is TRUE)

## User Entity

### Fields
- **id** (VARCHAR(255), NOT NULL) - Unique identifier for the user
- **email** (VARCHAR(255), NOT NULL) - User's email address
- **name** (VARCHAR(255), NULL) - User's display name
- **created_at** (TIMESTAMPTZ, DEFAULT NOW()) - Timestamp when user was registered
- **updated_at** (TIMESTAMPTZ, DEFAULT NOW()) - Timestamp when user was last updated

## Event Entity

### Fields
- **id** (UUID, PRIMARY KEY, DEFAULT gen_random_uuid()) - Unique identifier for the event
- **event_type** (VARCHAR(50), NOT NULL) - Type of event ('task.created', 'task.updated', 'task.completed', 'task.deleted', 'reminder.scheduled', etc.)
- **event_id** (UUID, NOT NULL) - Unique event identifier
- **timestamp** (TIMESTAMPTZ, DEFAULT NOW()) - When the event occurred
- **user_id** (VARCHAR(255), NOT NULL) - Identifier of the user associated with the event
- **task_id** (INTEGER, NULL) - Identifier of the task associated with the event (if applicable)
- **payload** (JSONB, NOT NULL) - Additional data specific to the event type

### Validation Rules
- Event type must be one of the predefined types
- Payload must conform to the schema for the specific event type

## Notification Entity

### Fields
- **id** (INTEGER, PRIMARY KEY, AUTO_INCREMENT) - Unique identifier for the notification
- **task_id** (INTEGER, NOT NULL) - Reference to the task that triggered the notification
- **user_id** (VARCHAR(255), NOT NULL) - Identifier of the user receiving the notification
- **title** (VARCHAR(255), NOT NULL) - Title of the notification
- **message** (TEXT, NOT NULL) - Content of the notification
- **channel** (VARCHAR(20), NOT NULL) - Delivery channel ('in_app', 'email', 'push', 'sms')
- **scheduled_at** (TIMESTAMPTZ, NOT NULL) - When the notification should be sent
- **sent_at** (TIMESTAMPTZ, NULL) - When the notification was actually sent
- **status** (VARCHAR(20), DEFAULT 'pending') - Current status ('pending', 'sent', 'failed')
- **created_at** (TIMESTAMPTZ, DEFAULT NOW()) - Timestamp when notification was created
- **updated_at** (TIMESTAMPTZ, DEFAULT NOW()) - Timestamp when notification was last updated

### Validation Rules
- Channel must be one of 'in_app', 'email', 'push', 'sms'
- Scheduled time must be in the future
- Status must be one of 'pending', 'sent', 'failed'

## Recurring Task Instance Entity

### Fields
- **id** (INTEGER, PRIMARY KEY, AUTO_INCREMENT) - Unique identifier for the recurring task instance
- **parent_task_id** (INTEGER, NOT NULL) - Reference to the original recurring task
- **original_due_date** (TIMESTAMPTZ, NOT NULL) - When this instance was originally scheduled
- **actual_due_date** (TIMESTAMPTZ, NOT NULL) - When this instance is actually due
- **status** (VARCHAR(20), DEFAULT 'pending') - Status of the instance ('pending', 'completed')
- **created_at** (TIMESTAMPTZ, DEFAULT NOW()) - Timestamp when instance was created
- **completed_at** (TIMESTAMPTZ, NULL) - Timestamp when instance was completed

### Validation Rules
- Actual due date must be after the parent task's creation date
- Parent task must have is_recurring set to TRUE