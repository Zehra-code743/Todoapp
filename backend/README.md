# Todo Application Backend

Phase II FastAPI backend with JWT authentication and PostgreSQL database.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ (or Neon account)
- pip (Python package manager)

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `DATABASE_URL`: Your PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Generate with `openssl rand -hex 32` (must match frontend)
- `CORS_ORIGINS`: Frontend URL (e.g., `http://localhost:3000`)

### 4. Run Database Migrations

Tables will be created automatically on first run (SQLModel create_all).

## Running Locally

```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start on: http://localhost:8000

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Testing

```bash
pytest
```

With coverage:
```bash
pytest --cov=src tests/
```

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── models/              # SQLModel entities
│   ├── schemas/             # Pydantic request/response models
│   ├── api/v1/              # API endpoints
│   ├── services/            # Business logic
│   └── middleware/          # JWT auth, CORS
├── tests/                   # pytest tests
└── requirements.txt         # Python dependencies
```

## API Endpoints

### Health
- `GET /health` - No auth required

### Tasks (Phase 4+)
- `GET /api/{user_id}/tasks` - List tasks
- `POST /api/{user_id}/tasks` - Create task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion
- `DELETE /api/{user_id}/tasks/{id}` - Delete task

All task endpoints require JWT token in Authorization header.

## Development

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Deployment

See root README.md for Vercel deployment instructions.
