# Quick Start Guide: Advanced Todo Features

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Apache Kafka
- Dapr runtime
- Docker and Docker Compose (for local development)

## Environment Setup

1. Install Dapr:
   ```bash
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
   dapr init
   ```

2. Set up PostgreSQL:
   ```bash
   docker run --name todo-postgres -p 5432:5432 -e POSTGRES_DB=todoapp -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -d postgres:13
   ```

3. Set up Kafka:
   ```bash
   docker-compose -f docker/kafka-docker-compose.yml up -d
   ```

## Local Development

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd todoapp
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```bash
   export DATABASE_URL=postgresql://postgres:password@localhost:5432/todoapp
   export KAFKA_BROKERS=localhost:9092
   export DAPR_HOST=localhost
   export DAPR_PORT=3500
   ```

5. Run database migrations:
   ```bash
   python -m scripts.migrate_db
   ```

6. Start the application:
   ```bash
   dapr run --app-id todo-api --app-port 8000 -- python -m src.main
   ```

## API Endpoints

### Task Management
- `GET /api/v1/tasks` - List all tasks with filtering and sorting options
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `POST /api/v1/tasks/{task_id}/complete` - Mark task as complete

### Recurring Tasks
- `POST /api/v1/recurring-tasks` - Create a recurring task
- `PUT /api/v1/recurring-tasks/{task_id}/pattern` - Update recurrence pattern

### Reminders
- `POST /api/v1/reminders/set-due-date` - Set due date and schedule reminder
- `POST /api/v1/reminders/snooze/{reminder_id}` - Snooze a reminder

### Search & Filter
- `GET /api/v1/search/tasks` - Search tasks by keyword and filters

## Dapr Components

The application uses the following Dapr components:

1. **State Store** (PostgreSQL): For persisting application state
2. **Pub/Sub** (Kafka): For event-driven communication between services
3. **Bindings**: For connecting to external systems

Configuration files are located in the `dapr-components/` directory.

## Testing

Run the test suite:
```bash
pytest tests/
```

Run specific test suites:
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
```

## Deployment

For Kubernetes deployment:
1. Install Dapr on your cluster: `dapr init --kubernetes`
2. Apply Kubernetes manifests: `kubectl apply -f k8s/`
3. Verify deployment: `kubectl get pods`