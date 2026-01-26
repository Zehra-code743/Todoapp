---
id: 1
title: advanced-todo-features-spec
stage: spec
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: advanced-cloud-deployment
branch: 2-advanced-cloud-deployment
user: claude
command: /sp.specify
labels: [specification, todo-app, advanced-features]
links:
  spec: ../specs/2-advanced-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/2-advanced-cloud-deployment/spec.md
 - specs/2-advanced-cloud-deployment/checklists/requirements.md
tests:
 - specs/2-advanced-cloud-deployment/spec.md validation
---
## Prompt

# Advanced Todo Features Specification

## Document Information
- **Phase**: V - Advanced Cloud Deployment
- **Feature Set**: Advanced Level + Intermediate Level
- **Technology Stack**: Event-Driven Architecture with Kafka + Dapr
- **Deployment**: Minikube (Local) → Azure/GCP/Oracle (Cloud)

---

## 1. Feature Overview

### 1.1 Advanced Level Features
- **Recurring Tasks**: Auto-reschedule repeating tasks
- **Due Dates & Time Reminders**: Set deadlines with notifications

### 1.2 Intermediate Level Features
- **Priorities & Tags/Categories**: Assign importance levels and labels
- **Search & Filter**: Find tasks by keyword, status, priority, date
- **Sort Tasks**: Reorder by multiple criteria

---

## 2. Advanced Feature: Recurring Tasks

### 2.1 User Stories
```
AS A user
I WANT to create tasks that repeat automatically
SO THAT I don't have to manually recreate weekly/daily tasks

AS A user
I WANT to customize recurrence patterns
SO THAT tasks match my actual schedule

AS A user
I WANT completed recurring tasks to spawn the next occurrence
SO THAT my schedule stays current
```

### 2.2 Recurrence Patterns
Support the following patterns:

| Pattern | Description | Example |
|---------|-------------|---------|
| Daily | Every day at specified time | "Take vitamins" |
| Weekly | Specific day(s) of week | "Team meeting every Monday" |
| Monthly | Specific day of month | "Pay rent on 1st" |
| Custom | Every N days/weeks/months | "Dentist every 6 months" |

### 2.3 Data Schema Extension

```typescript
interface RecurringTask extends Task {
  is_recurring: boolean
  recurrence_pattern: RecurrencePattern
  parent_task_id?: number  // Links to original recurring task
  next_occurrence_date?: datetime
}

interface RecurrencePattern {
  type: "daily" | "weekly" | "monthly" | "custom"
  interval: number  // e.g., every 2 weeks
  days_of_week?: number[]  // [0-6] for Sunday-Saturday
  day_of_month?: number  // 1-31
  end_condition?: {
    type: "never" | "after_n_occurrences" | "by_date"
    value?: number | datetime
  }
}
```

### 2.4 Business Rules

**BR-R1**: When a recurring task is marked complete:
- Current task remains completed
- System auto-creates next occurrence based on pattern
- Next occurrence inherits: title, description, recurrence_pattern
- Next occurrence does NOT inherit: completed status, completion_date

**BR-R2**: Editing a recurring task:
- User can choose: "This task only" OR "This and future tasks"
- "This and future tasks" updates the parent pattern

**BR-R3**: Deleting a recurring task:
- User can choose: "This task only" OR "All future tasks"
- Deleting parent cancels all future auto-generation

**BR-R4**: Skipping a recurring task:
- User can skip without completing
- System still generates next occurrence

### 2.5 Event-Driven Implementation (Kafka)

**Kafka Topic**: `task-events`

**Event Flow**:
```
1. User marks recurring task complete
   ↓
2. Chat API publishes event to Kafka
   {
     "event_type": "task.completed",
     "task_id": 123,
     "user_id": "user-abc",
     "is_recurring": true,
     "recurrence_pattern": {...},
     "completed_at": "2026-01-15T10:30:00Z"
   }
   ↓
3. Recurring Task Service consumes event
   ↓
4. Service calculates next_occurrence_date
   ↓
5. Service creates new task via MCP tool: add_task
   ↓
6. Service publishes confirmation event
```

### 2.6 MCP Tool Extensions

**New Tool**: `create_recurring_task`
```json
{
  "name": "create_recurring_task",
  "parameters": {
    "user_id": "string (required)",
    "title": "string (required)",
    "description": "string (optional)",
    "recurrence_pattern": {
      "type": "daily|weekly|monthly|custom",
      "interval": "number",
      "days_of_week": "array (optional)",
      "day_of_month": "number (optional)",
      "end_condition": "object (optional)"
    },
    "first_occurrence_date": "datetime (required)"
  }
}
```

**Modified Tool**: `complete_task`
- Add logic to check `is_recurring` flag
- Publish event to Kafka if true

### 2.7 Chatbot Natural Language Examples

| User Says | Agent Should |
|-----------|--------------|
| "Remind me to take vitamins every morning at 8 AM" | Create recurring task (daily, 8:00) |
| "Team standup every weekday at 9:30 AM" | Create recurring task (Mon-Fri, 9:30) |
| "Pay rent on the 1st of every month" | Create recurring task (monthly, day 1) |
| "Dentist checkup every 6 months" | Create recurring task (custom, 6 months) |
| "Stop the weekly report task" | Delete recurring task + all future |

---

## 3. Advanced Feature: Due Dates & Time Reminders

### 3.1 User Stories
```
AS A user
I WANT to set due dates and times for tasks
SO THAT I know when tasks need to be completed

AS A user
I WANT to receive reminders before tasks are due
SO THAT I don't forget important deadlines

AS A user
I WANT to customize reminder timing
SO THAT I get notified at the right moment
```

### 3.2 Data Schema Extension

```typescript
interface TaskWithReminders extends Task {
  due_date?: datetime
  reminder_settings?: ReminderSettings
  reminder_sent?: boolean
}

interface ReminderSettings {
  enabled: boolean
  advance_notice: number  // minutes before due_date
  notification_channels: ("email" | "push" | "in_app")[]
}
```

### 3.3 Business Rules

**BR-D1**: Due date can be set at task creation or added later

**BR-D2**: Default reminder timing:
- 15 minutes before (for tasks < 1 hour away)
- 1 hour before (for tasks 1-24 hours away)
- 1 day before (for tasks > 24 hours away)

**BR-D3**: User can customize reminder advance notice (5 min to 7 days)

**BR-D4**: Overdue tasks should be visually highlighted

**BR-D5**: Reminders are sent ONCE per task (idempotent)

### 3.4 Event-Driven Implementation (Kafka + Dapr)

**Architecture**:
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Chat API       │────▶│  Kafka Topic    │────▶│  Notification   │
│  (sets due_date)│     │  "reminders"    │     │  Service        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                  ┌─────────────────┐
                                                  │  Dapr Jobs API  │
                                                  │  (exact timing) │
                                                  └─────────────────┘
```

**Kafka Topic**: `reminders`

**Event Flow**:
```
1. User sets due date via chatbot: "Finish report by Friday 5 PM"
   ↓
2. Chat API creates task with due_date
   ↓
3. Chat API publishes to Kafka "reminders" topic
   {
     "event_type": "reminder.scheduled",
     "task_id": 456,
     "user_id": "user-abc",
     "title": "Finish report",
     "due_at": "2026-01-17T17:00:00Z",
     "remind_at": "2026-01-17T16:00:00Z",  // 1 hour before
     "channels": ["push", "email"]
   }
   ↓
4. Notification Service consumes event
   ↓
5. Service schedules via Dapr Jobs API
   await dapr_jobs.schedule(
     job_id="reminder-task-456",
     due_time="2026-01-17T16:00:00Z",
     callback_url="/api/jobs/trigger"
   )
   ↓
6. At scheduled time, Dapr triggers callback
   ↓
7. Notification Service sends push/email
   ↓
8. Service marks task.reminder_sent = true
```

### 3.5 Dapr Jobs API Implementation

**Schedule Reminder** (Python):
```python
import httpx
from datetime import datetime, timedelta

async def schedule_reminder(task_id: int, due_at: datetime, user_id: str):
    """Schedule exact-time reminder using Dapr Jobs API."""

    # Calculate reminder time (1 hour before)
    remind_at = due_at - timedelta(hours=1)

    await httpx.post(
        f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
        json={
            "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "type": "reminder",
                "due_at": due_at.isoformat()
            }
        }
    )
```

**Handle Callback** (FastAPI):
```python
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Dapr calls this endpoint at exact scheduled time."""
    job_data = await request.json()

    if job_data["data"]["type"] == "reminder":
        # Send notification via Pub/Sub
        await publish_event(
            topic="notifications",
            event_type="send.push",
            data=job_data["data"]
        )

    return {"status": "SUCCESS"}
```

### 3.6 MCP Tool Extensions

**New Tool**: `set_due_date`
```json
{
  "name": "set_due_date",
  "parameters": {
    "user_id": "string (required)",
    "task_id": "number (required)",
    "due_date": "datetime (required)",
    "reminder_enabled": "boolean (optional, default: true)",
    "reminder_advance_minutes": "number (optional, default: 60)"
  }
}
```

**New Tool**: `snooze_reminder`
```json
{
  "name": "snooze_reminder",
  "parameters": {
    "user_id": "string (required)",
    "task_id": "number (required)",
    "snooze_duration_minutes": "number (required)"
  }
}
```

### 3.7 Chatbot Natural Language Examples

| User Says | Agent Should |
|-----------|--------------|
| "Remind me to call mom tomorrow at 3 PM" | Create task with due_date, schedule reminder |
| "Finish the report by Friday 5 PM" | Set due_date, schedule reminder 1 hour before |
| "Snooze the meeting reminder for 15 minutes" | Reschedule reminder via Dapr Jobs |
| "What's due today?" | Filter tasks by due_date = today |
| "Show overdue tasks" | Filter tasks where due_date < now AND completed = false |

---

## 4. Intermediate Feature: Priorities & Tags

### 4.1 User Stories
```
AS A user
I WANT to assign priority levels to tasks
SO THAT I can focus on what's most important

AS A user
I WANT to categorize tasks with tags
SO THAT I can organize by context (work, personal, etc.)
```

### 4.2 Data Schema Extension

```typescript
interface TaskWithMetadata extends Task {
  priority: "low" | "medium" | "high" | "urgent"
  tags: string[]  // ["work", "urgent", "home"]
  category?: string  // Optional broader grouping
}
```

### 4.3 Business Rules

**BR-P1**: Default priority is "medium"

**BR-P2**: Tags are case-insensitive and normalized

**BR-P3**: Users can filter/sort by priority

**BR-P4**: Multiple tags allowed per task

### 4.4 MCP Tool Extensions

**Modified Tool**: `add_task`
```json
{
  "parameters": {
    "title": "string",
    "description": "string",
    "priority": "low|medium|high|urgent (optional)",
    "tags": "array of strings (optional)"
  }
}
```

**New Tool**: `update_priority`
```json
{
  "name": "update_priority",
  "parameters": {
    "user_id": "string (required)",
    "task_id": "number (required)",
    "priority": "low|medium|high|urgent (required)"
  }
}
```

**New Tool**: `add_tags`
```json
{
  "name": "add_tags",
  "parameters": {
    "user_id": "string (required)",
    "task_id": "number (required)",
    "tags": "array of strings (required)"
  }
}
```

### 4.5 Chatbot Natural Language Examples

| User Says | Agent Should |
|-----------|--------------|
| "High priority: Finish the proposal" | Create task with priority="high" |
| "Tag this task as work and urgent" | Add tags ["work", "urgent"] |
| "Show me all urgent tasks" | Filter by priority="urgent" |
| "What are my work tasks?" | Filter by tag="work" |

---

## 5. Intermediate Feature: Search & Filter

### 5.1 User Stories
```
AS A user
I WANT to search tasks by keyword
SO THAT I can quickly find specific items

AS A user
I WANT to filter by status, priority, tags, and date
SO THAT I can view relevant subsets
```

### 5.2 Search Capabilities

| Search Type | Field(s) | Example Query |
|-------------|----------|---------------|
| Keyword | title, description | "meeting" |
| Status | completed | "pending" OR "completed" |
| Priority | priority | "high" OR "urgent" |
| Tag | tags | "work" |
| Date Range | created_at, due_date | "last week" OR "next 3 days" |

### 5.3 MCP Tool Extensions

**New Tool**: `search_tasks`
```json
{
  "name": "search_tasks",
  "parameters": {
    "user_id": "string (required)",
    "keyword": "string (optional)",
    "status": "all|pending|completed (optional)",
    "priority": "low|medium|high|urgent (optional)",
    "tags": "array of strings (optional)",
    "due_date_range": {
      "start": "datetime (optional)",
      "end": "datetime (optional)"
    }
  }
}
```

### 5.4 Chatbot Natural Language Examples

| User Says | Agent Should |
|-----------|--------------|
| "Find tasks about the presentation" | search_tasks(keyword="presentation") |
| "Show high priority work tasks" | search_tasks(priority="high", tags=["work"]) |
| "What's due this week?" | search_tasks(due_date_range={start: today, end: +7 days}) |

---

## 6. Intermediate Feature: Sort Tasks

### 6.1 Sort Criteria

| Criterion | Order Options | Use Case |
|-----------|---------------|----------|
| Due Date | Ascending/Descending | See what's urgent first |
| Priority | High→Low / Low→High | Focus on important items |
| Created Date | Newest/Oldest | See recent additions |
| Title | A→Z / Z→A | Alphabetical organization |
| Completion Status | Completed first/last | Separate done from pending |

### 6.2 MCP Tool Extensions

**Modified Tool**: `list_tasks`
```json
{
  "parameters": {
    "user_id": "string (required)",
    "status": "all|pending|completed (optional)",
    "sort_by": "due_date|priority|created_at|title (optional)",
    "sort_order": "asc|desc (optional, default: asc)"
  }
}
```

### 6.3 Chatbot Natural Language Examples

| User Says | Agent Should |
|-----------|--------------|
| "Show tasks by priority" | list_tasks(sort_by="priority", sort_order="desc") |
| "What's due soonest?" | list_tasks(sort_by="due_date", sort_order="asc") |
| "Alphabetical list of tasks" | list_tasks(sort_by="title") |

---

## 7. Database Schema (Complete)

```sql
-- Extended tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,

    -- Advanced Features
    priority VARCHAR(20) DEFAULT 'medium',
    tags TEXT[],
    category VARCHAR(100),

    -- Recurring Tasks
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern JSONB,
    parent_task_id INTEGER REFERENCES tasks(id),
    next_occurrence_date TIMESTAMP,

    -- Due Dates & Reminders
    due_date TIMESTAMP,
    reminder_settings JSONB,
    reminder_sent BOOLEAN DEFAULT FALSE,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_priority (priority),
    INDEX idx_tags (tags),
    INDEX idx_due_date (due_date),
    INDEX idx_recurring (is_recurring),
    INDEX idx_completed (completed)
);

-- Reminder schedule table
CREATE TABLE reminder_schedules (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, sent, cancelled
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 8. Testing Scenarios

### 8.1 Recurring Tasks Tests

```gherkin
Scenario: Daily recurring task
  Given I create a recurring task "Take vitamins" (daily, 8:00 AM)
  When I complete today's instance
  Then tomorrow's instance should be auto-created at 8:00 AM

Scenario: Weekly team meeting
  Given I create "Team standup" (every Monday, 9:30 AM)
  When Monday arrives and task completes
  Then next Monday's instance should exist

Scenario: Stop recurring task
  Given I have "Weekly report" recurring every Friday
  When I delete with "All future tasks" option
  Then no future instances should exist
```

### 8.2 Reminder Tests

```gherkin
Scenario: Reminder sent on time
  Given I have task "Meeting" due at 3:00 PM today
  And reminder set for 1 hour before
  When clock reaches 2:00 PM
  Then I should receive a notification

Scenario: Snooze reminder
  Given I receive a reminder for task "Call client"
  When I snooze for 15 minutes
  Then reminder should retrigger in 15 minutes
```

### 8.3 Filter & Search Tests

```gherkin
Scenario: Search by keyword
  Given I have tasks: "Buy groceries", "Schedule meeting", "Grocery shopping"
  When I search for "grocer"
  Then I should see 2 results

Scenario: Filter high priority work tasks
  Given I have 10 tasks with various priorities and tags
  When I filter by priority=high AND tag=work
  Then I should see only high priority work tasks
```

---

## 9. Acceptance Criteria

### 9.1 Recurring Tasks
- [ ] User can create tasks with daily/weekly/monthly patterns
- [ ] Completed recurring tasks auto-spawn next occurrence
- [ ] User can edit "this task only" or "this and future"
- [ ] User can delete individual or all future occurrences
- [ ] Recurring Task Service consumes Kafka events
- [ ] Next occurrence calculation is accurate

### 9.2 Due Dates & Reminders
- [ ] User can set due dates via natural language
- [ ] Reminders trigger at correct time (via Dapr Jobs)
- [ ] Notification Service sends push/email
- [ ] Overdue tasks are visually highlighted
- [ ] User can customize reminder timing
- [ ] Reminders are idempotent (sent once)

### 9.3 Priorities & Tags
- [ ] User can assign priority levels
- [ ] User can add/remove tags
- [ ] Tasks can be filtered by priority
- [ ] Tasks can be filtered by tags
- [ ] Chatbot understands priority keywords

### 9.4 Search & Filter
- [ ] Keyword search works on title + description
- [ ] Filter by status works
- [ ] Filter by priority works
- [ ] Filter by tags works
- [ ] Date range filtering works
- [ ] Multiple filters can be combined

### 9.5 Sort
- [ ] Sort by due date (asc/desc)
- [ ] Sort by priority (high→low / low→high)
- [ ] Sort by created date
- [ ] Sort alphabetically
- [ ] Sort order persists across sessions

---

## 10. Implementation Checklist

### Phase V - Part A (Advanced Features)
- [ ] Update database schema with new fields
- [ ] Create Recurring Task Service (Kafka consumer)
- [ ] Implement Notification Service (Kafka consumer)
- [ ] Integrate Dapr Jobs API for reminders
- [ ] Extend MCP tools with new parameters
- [ ] Update chatbot prompts for advanced commands
- [ ] Add event publishing to Chat API

### Phase V - Part B (Local Deployment)
- [ ] Deploy Kafka on Minikube (Strimzi or Redpanda)
- [ ] Install Dapr on Minikube
- [ ] Configure Dapr Pub/Sub component (Kafka)
- [ ] Configure Dapr Jobs component
- [ ] Deploy all services with Helm charts
- [ ] Test end-to-end event flow locally

### Phase V - Part C (Cloud Deployment)
- [ ] Provision AKS/GKE/OKE cluster
- [ ] Set up Redpanda Cloud or managed Kafka
- [ ] Deploy Dapr on cloud cluster
- [ ] Configure Dapr components for production
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure monitoring (logs, metrics)
- [ ] Load test with concurrent users

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| Recurring task accuracy | 100% correct next occurrence |
| Reminder delivery latency | < 30 seconds from scheduled time |
| Search response time | < 200ms for 10,000 tasks |
| Filter accuracy | 100% correct results |
| Event processing lag | < 5 seconds (Kafka → Service) |
| System uptime | 99.9% |

---

## 12. Non-Functional Requirements

**NFR-1**: All services must be stateless for horizontal scaling

**NFR-2**: Kafka events must be idempotent (replayable)

**NFR-3**: Database queries must use indexes (no full table scans)

**NFR-4**: Reminder scheduling must survive service restarts (Dapr handles this)

**NFR-5**: API response time p95 < 500ms

**NFR-6**: System must handle 100 concurrent users

---

## 13. Future Enhancements (Out of Scope)

- AI-powered task prioritization
- Collaborative task sharing
- Mobile app (native iOS/Android)
- Voice input/output
- Calendar integration (Google Calendar, Outlook)
- Smart scheduling (AI suggests best time)

## Response snapshot

I have successfully created a comprehensive feature specification for the Advanced Todo Features. The specification includes:

1. Detailed user stories for all main features:
   - Recurring Tasks (P1 priority)
   - Due Dates & Time Reminders (P1 priority)
   - Priorities & Tags (P2 priority)
   - Search & Filter (P2 priority)
   - Sort Tasks (P3 priority)

2. Functional requirements covering all aspects of the feature set

3. Key entities that represent the data model

4. Technology-agnostic success criteria with measurable outcomes

5. Edge cases that need consideration

6. A validation checklist that confirms the specification meets quality standards

The specification is stored in specs/2-advanced-cloud-deployment/spec.md and follows the required template structure. It avoids implementation details while focusing on user value and business needs.

## Outcome

- ✅ Impact: Created comprehensive specification for advanced todo features including recurring tasks, due dates, reminders, priorities, tags, search and sort capabilities
- 🧪 Tests: Specification validated against quality checklist with all items passing
- 📁 Files: Created spec.md and requirements checklist in checklists directory
- 🔁 Next prompts: Ready for planning phase (/sp.plan) or clarification phase (/sp.clarify)
- 🧠 Reflection: Specification successfully abstracts implementation details while capturing all essential user requirements

## Evaluation notes (flywheel)

- Failure modes observed: None - all specification requirements met
- Graders run and results (PASS/FAIL): PASS - all validation criteria satisfied
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase