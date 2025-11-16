# TODO Application

A personal TODO application with Streamlit UI, PostgreSQL database, and comprehensive task management features.

![TODO App Interface](./report/ui.png)

## Features

- **CRUD Operations**: Create, read, update, and delete tasks
- **Task Attributes**:
  - Title and description
  - Priority levels (High, Medium, Low)
  - Due dates and start dates
  - Time estimates
  - Repeat intervals (hourly, daily, weekly, monthly)
  - Tags for categorization
- **Filtering**: Filter tasks by completion status, priority, and tags
- **Clean Architecture**: Separation of concerns with database, service, and UI layers

## Tech Stack

- **Frontend**: Streamlit
- **Database**: PostgreSQL 16
- **ORM**: SQLModel
- **Configuration**: pydantic-settings
- **Testing**: pytest
- **Package Manager**: uv
- **Orchestration**: Docker Compose

## What's Included

- ✅ Complete CRUD operations with Streamlit UI
- ✅ Unit tests and integration tests with PostgreSQL
- ✅ CI/CD workflows (GitHub Actions)
- ✅ Docker containerization with docker-compose
- ✅ Database initialization and seeding
- ✅ Strict type checking (mypy --strict)
- ✅ Code linting and formatting (ruff)
- ✅ Code coverage reporting

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional) [uv](https://docs.astral.sh/uv/getting-started/installation/) for local development

### Run with Docker Compose

1. Clone the repository
2. Start the application:

```bash
docker-compose up --build
```

3. Access the app at `http://localhost:8501`

**Note:** Database tables and seed data (default tags: work, personal, urgent, learning, health) are created automatically on first run.

### Local Development

1. Install dependencies:

```bash
uv sync --extra dev
```

2. Start PostgreSQL (using Docker):

```bash
docker-compose up postgres -d
```

3. Initialize the database:

```bash
uv run python -m src.db.init_db
uv run python -m src.db.seed
```

4. Run the application:

```bash
uv run streamlit run src/app.py
```

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=src tests/

# Run specific test file
uv run pytest tests/test_models.py -v
```

### Code Quality

```bash
# Check code
uvx ruff check src/ tests/

# Format code
uvx ruff format src/ tests/
```

## Environment Variables

Create a `.env` file (see `.env.example`):

```env
# Application
APP_NAME=TODO App

# Database
DATABASE_URL=postgresql://todo:todo@localhost:5432/tododb
DATABASE_ECHO=false

# PostgreSQL (for Docker)
POSTGRES_USER=todo
POSTGRES_PASSWORD=todo
POSTGRES_DB=tododb
```

## Database Schema

### Task Table
- `id`: Primary key
- `title`: Task title
- `description`: Optional description
- `completed`: Completion status
- `priority`: HIGH, MEDIUM, LOW
- `created_at`, `updated_at`: Timestamps
- `due_date`, `start_date`: Optional dates
- `completed_at`: Completion timestamp
- `time_estimate_minutes`: Time estimate
- `repeat_interval`: HOURLY, DAILY, WEEKLY, MONTHLY

### Tag Table
- `id`: Primary key
- `name`: Unique tag name
- `color`: Hex color code

### TaskTagLink Table
- Many-to-many relationship between tasks and tags

## Development Principles

This project follows clean code principles:
- **Separation of Concerns (SoC)**: Database, service, and UI layers
- **DRY (Don't Repeat Yourself)**: Reusable functions
- **KISS (Keep It Simple)**: Simple, maintainable code
- **YAGNI (You Ain't Gonna Need It)**: Only necessary features
- **TDD (Test-Driven Development)**: Comprehensive test coverage

## Troubleshooting

### Port 5432 already in use

```bash
# Stop existing PostgreSQL containers
docker-compose down

# Or change the port in docker-compose.yml:
# ports:
#   - "5433:5432"
```

### Database connection error

Verify that:
- PostgreSQL container is running: `docker-compose ps`
- `.env` file exists with correct `DATABASE_URL`
- `DATABASE_URL` matches credentials in `docker-compose.yml`

### Integration tests failing

```bash
# Ensure PostgreSQL is running
docker-compose up postgres -d

# Initialize the database
export DATABASE_URL=postgresql://todo:todo@localhost:5432/tododb
uv run python -m src.db.init_db

# Run tests
uv run pytest tests/integration_tests -v
```

### Docker build issues

```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## License

MIT
