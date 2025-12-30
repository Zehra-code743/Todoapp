# Todo Application - Spec-Driven Development Evolution

A multi-phase todo application demonstrating spec-driven development with Claude Code. This project evolves from a simple console app (Phase I) to a cloud-native AI-powered system (Phase V).

## Current Phase: Phase II - Full-Stack Web Application ✅ Complete

Multi-user web application with authentication, persistent storage, and RESTful API.

## Phase Evolution

### ✅ Phase I: Console Application (Complete)
- In-memory task storage
- Command-line interface
- Single-user CRUD operations

### ✅ Phase II: Web Application (Complete)
- ✅ JWT-based authentication (signup, signin, logout)
- ✅ Multi-user support with data isolation
- ✅ PostgreSQL persistent storage
- ✅ FastAPI RESTful backend
- ✅ Next.js React frontend with Tailwind CSS
- ✅ Full CRUD operations (Create, View, Update, Delete tasks)
- ✅ Optimistic UI updates with React Query
- ✅ Responsive design (mobile-first)
- ✅ Inline task editing with keyboard shortcuts
- ✅ Delete confirmation dialogs

### 📋 Phase III: AI Integration (Planned)
- Natural language task creation
- AI chatbot interface
- Intelligent task suggestions

### 📋 Phase IV: Cloud-Native (Planned)
- Kubernetes deployment
- Event-driven architecture
- Horizontal scaling

### 📋 Phase V: Advanced Features (Planned)
- Task priorities and tags
- Due dates and reminders
- Search and filtering
- Team collaboration

## Requirements

### Phase I (Console App)
- Python 3.11+
- UV Package Manager

### Phase II (Web Application)
- **Node.js**: 18.x or 20.x (LTS)
- **Python**: 3.11+
- **PostgreSQL**: 15+ (or Neon account)
- **Git**: Latest version

## Quick Start - Phase II Web Application

### 1. Clone and Checkout

```bash
git clone <repository-url>
cd Todoapp
git checkout 002-phase-ii-fullstack-web
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set DATABASE_URL and BETTER_AUTH_SECRET
```

### 3. Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local and set BETTER_AUTH_SECRET (must match backend)
```

### 4. Start Database (Local Development)

```bash
# From project root
docker-compose up -d
```

Or use Neon PostgreSQL (recommended).

### 5. Run Application

**Option 1: One Command (Recommended) 🚀**

Run both frontend and backend together:

```bash
# Using batch file (Windows)
.\dev.bat

# Or using PowerShell script
.\dev.ps1

# Or using npm (after installing dependencies)
npm install  # Install concurrently
npm run dev
```

This will start both servers in separate windows/terminals.

**Option 2: Separate Terminals**

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Access Application**: http://localhost:3000

- Health Check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

## Phase II Features

### User Stories Implemented

1. **User Authentication (P1)**
   - Sign up with email, name, password
   - Sign in with credentials
   - Logout functionality
   - JWT tokens with 7-day expiration
   - httpOnly cookie storage for security

2. **Create and View Tasks (P2)**
   - Create tasks with title and optional description
   - View personal task list (newest first)
   - Task count statistics (total, pending, completed)
   - Empty state with helpful prompts
   - Real-time optimistic UI updates

3. **Mark Tasks Complete (P3)**
   - Toggle checkbox to mark complete/pending
   - Visual feedback (strikethrough, muted colors)
   - Instant UI updates before server confirmation
   - Smooth animations

4. **Edit Task Details (P4)**
   - Inline editing mode
   - Update title and description
   - Keyboard shortcuts (Enter to save, Escape to cancel)
   - Character count indicators
   - Validation with error messages

5. **Delete Tasks (P5)**
   - Delete button with confirmation dialog
   - Shows task title in confirmation
   - Optimistic removal from UI
   - Rollback on failure

### Technical Highlights

- **Security**: User data isolation, JWT validation on every request, bcrypt password hashing
- **Performance**: <100ms optimistic updates, <500ms API p95, indexed database queries
- **UX**: Mobile-responsive, keyboard shortcuts, loading states, error messages
- **Architecture**: Separation of concerns, TypeScript type safety, Pydantic validation

## Phase I Console App (Legacy)

### Running Phase I

```bash
git checkout 001-todo-console-app
uv sync
uv run python -m src.main
```

### Menu Options

```
Todo Console App
==================================================
1. Add Task
2. View Tasks
3. Mark Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit
==================================================
```

### Example Workflow

```bash
# Launch the app
uv run python -m src.main

# Select 1 to add a task
Select option: 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
✓ Task #1 'Buy groceries' created successfully

# Select 2 to view tasks
Select option: 2

================================================================================
ID   | Status   | Title                     | Description
--------------------------------------------------------------------------------
1    | ○ Pending | Buy groceries             | Milk, eggs, bread
================================================================================

# Select 3 to mark complete
Select option: 3
Enter task ID: 1
✓ Task #1 marked as completed

# Select 6 to exit
Select option: 6
Application closed. Goodbye!
```

## Testing

### Run All Tests

```bash
uv run pytest
```

### Run Tests with Coverage

```bash
uv run pytest --cov=src --cov-report=term
```

### Test Coverage

- **Task Entity**: 100% coverage (28/28 statements)
- **TaskManager**: 62% coverage (business logic tested)
- **Total**: 43 tests passing

## Project Structure

```
Todoapp/
├── src/
│   ├── __init__.py          # Package marker
│   ├── main.py              # Entry point & menu system
│   ├── task.py              # Task dataclass (100% coverage)
│   ├── manager.py           # TaskManager CRUD operations
│   └── ui.py                # Console I/O helpers
├── tests/
│   ├── unit/
│   │   ├── test_task.py     # Task entity tests (17 tests)
│   │   ├── test_manager.py  # Manager tests (21 tests)
│   │   └── test_ui.py       # UI helper tests (5 tests)
│   └── integration/
│       └── test_full_workflow.py  # End-to-end tests (5 tests)
├── specs/
│   └── 001-todo-console-app/
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       ├── tasks.md         # Task breakdown
│       └── ... (design docs)
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Known Limitations (Phase I)

- **In-Memory Only**: Tasks are stored in memory and lost when the application exits
- **Single User**: No authentication or multi-user support
- **No Persistence**: No file or database storage
- **No Due Dates**: Tasks don't have deadlines
- **No Priorities**: All tasks have equal priority
- **No Search/Filter**: Must view all tasks at once

These limitations are intentional for Phase I and will be addressed in future phases.

## Development

### Code Quality

- **Style Guide**: PEP 8
- **Type Hints**: All functions have type annotations
- **Docstrings**: All functions documented
- **Max Function Length**: 30 lines
- **No Global Variables**: Class or function scope only

### Architecture

- **Data Model**: `Task` dataclass with validation
- **Business Logic**: `TaskManager` class with CRUD operations
- **Presentation**: `ui.py` helper functions for console I/O
- **Entry Point**: `main.py` with menu system

## Troubleshooting

### ModuleNotFoundError: No module named 'src'

**Solution**: Run from repository root with module syntax:

```bash
cd D:/Todoapp
uv run python -m src.main
```

### UnicodeEncodeError

**Solution**: Ensure terminal supports UTF-8. On Windows, run:

```bash
chcp 65001
```

### UV command not found

**Solution**: Install UV:

```bash
# Unix/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Next Steps

- **Phase II**: File-based persistence
- **Phase III**: Database integration with multi-user support
- **Phase IV**: Web interface
- **Phase V**: AI-powered features

## License

This project is part of the Todo Evolution hackathon demonstrating spec-driven development with Claude Code.

## Contributing

This project follows strict spec-driven development:
1. All specifications in `/specs` directory
2. All code generated by Claude Code
3. No manual coding (AI-driven implementation)

For changes, update specifications first, then regenerate code.

---

**Version**: 1.0.0 (Phase I)
**Status**: ✅ Complete
**Last Updated**: 2025-12-25
