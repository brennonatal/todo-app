# TODO Application Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete personal TODO application with Streamlit UI, PostgreSQL database, and comprehensive task management features.

**Architecture:** Three-layer architecture with database functions (raw CRUD), service layer (business logic), and Streamlit UI. PostgreSQL runs in Docker with automatic initialization. SQLModel handles ORM, pydantic-settings manages configuration.

**Tech Stack:** Python, Streamlit, PostgreSQL, Docker Compose, SQLModel, pydantic-settings, pytest, uv (package manager)

---

## Task 1: Project Initialization and Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.gitignore`

**Step 1: Create Python version file**

Create `.python-version`:
```
3.12
```

**Step 2: Initialize uv project**

Run: `uv init --no-workspace`
Expected: Project initialized

**Step 3: Create pyproject.toml with dependencies**

Create `pyproject.toml`:
```toml
[project]
name = "todo-app"
version = "0.1.0"
description = "Personal TODO application with Streamlit UI"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "streamlit>=1.31.0",
    "sqlmodel>=0.0.14",
    "psycopg2-binary>=2.9.9",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
```

**Step 4: Create .gitignore**

Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
.pytest_cache/
.ruff_cache/

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite3
postgres_data/

# OS
.DS_Store
Thumbs.db
```

**Step 5: Install dependencies**

Run: `uv sync --extra dev`
Expected: Dependencies installed successfully

**Step 6: Commit**

Run:
```bash
git add .python-version pyproject.toml .gitignore
git commit -m "feat: initialize project with dependencies"
```

---

## Task 2: Environment Configuration with pydantic-settings

**Files:**
- Create: `src/settings.py`
- Create: `.env.example`

**Step 1: Write the failing test**

Create `tests/test_settings.py`:
```python
from src.settings import Settings


def test_settings_loads_from_env(monkeypatch):
    """Test that settings load from environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
    monkeypatch.setenv("DATABASE_ECHO", "true")

    settings = Settings()

    assert settings.database_url == "postgresql://test:test@localhost:5432/testdb"
    assert settings.database_echo is True


def test_settings_has_defaults():
    """Test that settings have reasonable defaults."""
    settings = Settings()

    assert settings.app_name == "TODO App"
    assert settings.database_echo is False
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_settings.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.settings'"

**Step 3: Create src directory and settings module**

Run: `mkdir -p src`

Create `src/__init__.py`:
```python
"""TODO application package."""
```

Create `src/settings.py`:
```python
"""Application settings using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "TODO App"

    # Database
    database_url: str = "postgresql://todo:todo@localhost:5432/tododb"
    database_echo: bool = False

    # Docker database (used in Docker Compose)
    postgres_user: str = "todo"
    postgres_password: str = "todo"
    postgres_db: str = "tododb"


# Global settings instance
settings = Settings()
```

**Step 4: Create .env.example**

Create `.env.example`:
```
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

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_settings.py -v`
Expected: PASS (2 tests)

**Step 6: Commit**

Run:
```bash
git add src/ tests/test_settings.py .env.example
git commit -m "feat: add settings with pydantic-settings"
```

---

## Task 3: Database Models with SQLModel

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

**Step 1: Write the failing test**

Create `tests/test_models.py`:
```python
import pytest
from datetime import datetime, timedelta
from src.models import Task, Tag, Priority, RepeatInterval


def test_task_creation():
    """Test creating a basic task."""
    task = Task(title="Test Task", description="Test Description")

    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert task.priority == Priority.MEDIUM


def test_task_with_all_fields():
    """Test creating a task with all optional fields."""
    now = datetime.now()
    due = now + timedelta(days=1)

    task = Task(
        title="Complete Task",
        description="Full description",
        completed=True,
        priority=Priority.HIGH,
        due_date=due,
        start_date=now,
        time_estimate_minutes=30,
        repeat_interval=RepeatInterval.DAILY,
    )

    assert task.completed is True
    assert task.priority == Priority.HIGH
    assert task.due_date == due
    assert task.time_estimate_minutes == 30


def test_tag_creation():
    """Test creating a tag."""
    tag = Tag(name="work", color="#FF0000")

    assert tag.name == "work"
    assert tag.color == "#FF0000"


def test_priority_enum():
    """Test priority enum values."""
    assert Priority.LOW == "low"
    assert Priority.MEDIUM == "medium"
    assert Priority.HIGH == "high"


def test_repeat_interval_enum():
    """Test repeat interval enum values."""
    assert RepeatInterval.HOURLY == "hourly"
    assert RepeatInterval.DAILY == "daily"
    assert RepeatInterval.WEEKLY == "weekly"
    assert RepeatInterval.MONTHLY == "monthly"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.models'"

**Step 3: Create models module**

Create `src/models.py`:
```python
"""Database models using SQLModel."""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RepeatInterval(str, Enum):
    """Task repeat intervals."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskTagLink(SQLModel, table=True):
    """Many-to-many relationship between tasks and tags."""
    __tablename__ = "task_tag_link"

    task_id: int = Field(foreign_key="task.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class Tag(SQLModel, table=True):
    """Tag model for categorizing tasks."""
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50)
    color: str = Field(max_length=7, default="#808080")  # Hex color

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)


class Task(SQLModel, table=True):
    """Task model with all TODO features."""
    __tablename__ = "task"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, index=True)

    # Priority
    priority: Priority = Field(default=Priority.MEDIUM, index=True)

    # Dates
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = Field(default=None, index=True)
    start_date: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    # Time estimate in minutes
    time_estimate_minutes: Optional[int] = Field(default=None)

    # Repeat functionality
    repeat_interval: Optional[RepeatInterval] = Field(default=None)

    # Relationships
    tags: list[Tag] = Relationship(back_populates="tasks", link_model=TaskTagLink)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py -v`
Expected: PASS (5 tests)

**Step 5: Commit**

Run:
```bash
git add src/models.py tests/test_models.py
git commit -m "feat: add database models with SQLModel"
```

---

## Task 4: Database Engine and Session Management

**Files:**
- Create: `src/db/__init__.py`
- Create: `src/db/engine.py`
- Create: `tests/test_db_engine.py`

**Step 1: Write the failing test**

Create `tests/test_db_engine.py`:
```python
import pytest
from sqlmodel import Session
from src.db.engine import get_engine, get_session


def test_get_engine():
    """Test that get_engine returns a valid engine."""
    engine = get_engine()

    assert engine is not None
    assert hasattr(engine, "url")


def test_get_session():
    """Test that get_session returns a valid session."""
    with get_session() as session:
        assert isinstance(session, Session)
        assert session.bind is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db_engine.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.db'"

**Step 3: Create database engine module**

Create `src/db/__init__.py`:
```python
"""Database package."""
from src.db.engine import get_engine, get_session

__all__ = ["get_engine", "get_session"]
```

Create `src/db/engine.py`:
```python
"""Database engine and session management."""
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, create_engine

from src.settings import settings


def get_engine():
    """Create and return database engine."""
    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,  # Verify connections before using
    )


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_db_engine.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

Run:
```bash
git add src/db/ tests/test_db_engine.py
git commit -m "feat: add database engine and session management"
```

---

## Task 5: Database Initialization Script

**Files:**
- Create: `src/db/init_db.py`

**Step 1: Create database initialization script**

Create `src/db/init_db.py`:
```python
"""Database initialization script - creates all tables."""
from sqlmodel import SQLModel

from src.db.engine import get_engine
from src.models import Task, Tag, TaskTagLink  # noqa: F401 - needed for table creation


def init_db() -> None:
    """Initialize database by creating all tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")


if __name__ == "__main__":
    init_db()
```

**Step 2: Test the initialization script manually**

Run: `uv run python -m src.db.init_db`
Expected: "Database tables created successfully" (Note: requires running PostgreSQL)

**Step 3: Commit**

Run:
```bash
git add src/db/init_db.py
git commit -m "feat: add database initialization script"
```

---

## Task 6: Database Seed Script for Initial Tags

**Files:**
- Create: `src/db/seed.py`

**Step 1: Create seed script**

Create `src/db/seed.py`:
```python
"""Database seeding script - creates initial tags."""
from sqlmodel import select

from src.db.engine import get_session
from src.models import Tag


def seed_initial_tags() -> None:
    """Create initial tags if they don't exist."""
    initial_tags = [
        Tag(name="work", color="#3B82F6"),      # Blue
        Tag(name="personal", color="#10B981"),  # Green
        Tag(name="urgent", color="#EF4444"),    # Red
        Tag(name="learning", color="#8B5CF6"),  # Purple
        Tag(name="health", color="#F59E0B"),    # Orange
    ]

    with get_session() as session:
        for tag_data in initial_tags:
            # Check if tag already exists
            statement = select(Tag).where(Tag.name == tag_data.name)
            existing_tag = session.exec(statement).first()

            if not existing_tag:
                session.add(tag_data)
                print(f"Created tag: {tag_data.name}")
            else:
                print(f"Tag already exists: {tag_data.name}")

        session.commit()

    print("Database seeding completed")


if __name__ == "__main__":
    seed_initial_tags()
```

**Step 2: Test the seed script manually**

Run: `uv run python -m src.db.seed`
Expected: "Created tag: work", "Created tag: personal", etc.

**Step 3: Commit**

Run:
```bash
git add src/db/seed.py
git commit -m "feat: add database seed script for initial tags"
```

---

## Task 7: CRUD Functions - Create Task

**Files:**
- Create: `src/db/functions/__init__.py`
- Create: `src/db/functions/create_task.py`
- Create: `tests/test_db_create_task.py`

**Step 1: Write the failing test**

Create `tests/test_db_create_task.py`:
```python
import pytest
from datetime import datetime, timedelta
from src.db.functions.create_task import create_task
from src.db.engine import get_session
from src.models import Task, Priority


def test_create_basic_task():
    """Test creating a basic task."""
    task = create_task(
        title="Test Task",
        description="Test Description"
    )

    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False

    # Cleanup
    with get_session() as session:
        session.delete(task)


def test_create_task_with_priority():
    """Test creating a task with priority."""
    task = create_task(
        title="High Priority Task",
        priority=Priority.HIGH
    )

    assert task.priority == Priority.HIGH

    # Cleanup
    with get_session() as session:
        session.delete(task)


def test_create_task_with_dates():
    """Test creating a task with due date and start date."""
    now = datetime.now()
    due = now + timedelta(days=1)

    task = create_task(
        title="Scheduled Task",
        due_date=due,
        start_date=now
    )

    assert task.due_date == due
    assert task.start_date == now

    # Cleanup
    with get_session() as session:
        session.delete(task)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db_create_task.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.db.functions'"

**Step 3: Create the create_task function**

Create `src/db/functions/__init__.py`:
```python
"""Database CRUD functions."""
from src.db.functions.create_task import create_task

__all__ = ["create_task"]
```

Create `src/db/functions/create_task.py`:
```python
"""Create task database function."""
from datetime import datetime
from typing import Optional

from src.db.engine import get_session
from src.models import Task, Priority, RepeatInterval


def create_task(
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.MEDIUM,
    due_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    time_estimate_minutes: Optional[int] = None,
    repeat_interval: Optional[RepeatInterval] = None,
) -> Task:
    """
    Create a new task in the database.

    Args:
        title: Task title (required)
        description: Task description
        priority: Task priority level
        due_date: When task is due
        start_date: When to start the task
        time_estimate_minutes: Estimated time to complete
        repeat_interval: How often task repeats

    Returns:
        Created Task object with assigned ID
    """
    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        start_date=start_date,
        time_estimate_minutes=time_estimate_minutes,
        repeat_interval=repeat_interval,
    )

    with get_session() as session:
        session.add(task)
        session.commit()
        session.refresh(task)

    return task
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_db_create_task.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

Run:
```bash
git add src/db/functions/ tests/test_db_create_task.py
git commit -m "feat: add create_task database function"
```

---

## Task 8: CRUD Functions - List Tasks

**Files:**
- Create: `src/db/functions/list_tasks.py`
- Modify: `src/db/functions/__init__.py`
- Create: `tests/test_db_list_tasks.py`

**Step 1: Write the failing test**

Create `tests/test_db_list_tasks.py`:
```python
import pytest
from datetime import datetime, timedelta
from src.db.functions.create_task import create_task
from src.db.functions.list_tasks import list_tasks
from src.db.engine import get_session
from src.models import Task, Priority


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    tasks = [
        create_task(title="Task 1", priority=Priority.HIGH, completed=False),
        create_task(title="Task 2", priority=Priority.LOW, completed=True),
        create_task(title="Task 3", priority=Priority.MEDIUM, completed=False),
    ]
    yield tasks

    # Cleanup
    with get_session() as session:
        for task in tasks:
            session.delete(task)


def test_list_all_tasks(sample_tasks):
    """Test listing all tasks."""
    tasks = list_tasks()

    assert len(tasks) >= 3
    task_titles = [t.title for t in tasks]
    assert "Task 1" in task_titles
    assert "Task 2" in task_titles


def test_list_tasks_filter_by_completed(sample_tasks):
    """Test filtering tasks by completion status."""
    incomplete_tasks = list_tasks(completed=False)

    assert len(incomplete_tasks) >= 2
    assert all(not task.completed for task in incomplete_tasks)


def test_list_tasks_filter_by_priority(sample_tasks):
    """Test filtering tasks by priority."""
    high_priority_tasks = list_tasks(priority=Priority.HIGH)

    assert len(high_priority_tasks) >= 1
    assert all(task.priority == Priority.HIGH for task in high_priority_tasks)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db_list_tasks.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.db.functions.list_tasks'"

**Step 3: Create the list_tasks function**

Create `src/db/functions/list_tasks.py`:
```python
"""List tasks database function."""
from typing import Optional

from sqlmodel import select

from src.db.engine import get_session
from src.models import Task, Priority


def list_tasks(
    completed: Optional[bool] = None,
    priority: Optional[Priority] = None,
) -> list[Task]:
    """
    List tasks with optional filters.

    Args:
        completed: Filter by completion status (None = all tasks)
        priority: Filter by priority level (None = all priorities)

    Returns:
        List of Task objects matching the filters
    """
    with get_session() as session:
        statement = select(Task)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        if priority is not None:
            statement = statement.where(Task.priority == priority)

        # Order by: incomplete first, then by due date, then by priority
        statement = statement.order_by(
            Task.completed,
            Task.due_date.nulls_last(),
            Task.priority.desc()
        )

        tasks = session.exec(statement).all()

    return list(tasks)
```

**Step 4: Modify __init__.py to export new function**

Modify `src/db/functions/__init__.py`:
```python
"""Database CRUD functions."""
from src.db.functions.create_task import create_task
from src.db.functions.list_tasks import list_tasks

__all__ = ["create_task", "list_tasks"]
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_db_list_tasks.py -v`
Expected: PASS (3 tests)

**Step 6: Commit**

Run:
```bash
git add src/db/functions/list_tasks.py src/db/functions/__init__.py tests/test_db_list_tasks.py
git commit -m "feat: add list_tasks database function with filters"
```

---

## Task 9: CRUD Functions - Edit Task

**Files:**
- Create: `src/db/functions/edit_task.py`
- Modify: `src/db/functions/__init__.py`
- Create: `tests/test_db_edit_task.py`

**Step 1: Write the failing test**

Create `tests/test_db_edit_task.py`:
```python
import pytest
from datetime import datetime, timedelta
from src.db.functions.create_task import create_task
from src.db.functions.edit_task import edit_task
from src.db.engine import get_session
from src.models import Task, Priority


def test_edit_task_title():
    """Test editing a task title."""
    task = create_task(title="Original Title")

    updated_task = edit_task(task.id, title="New Title")

    assert updated_task.title == "New Title"
    assert updated_task.id == task.id

    # Cleanup
    with get_session() as session:
        session.delete(updated_task)


def test_edit_task_completion():
    """Test marking a task as completed."""
    task = create_task(title="Test Task", completed=False)

    updated_task = edit_task(task.id, completed=True)

    assert updated_task.completed is True
    assert updated_task.completed_at is not None

    # Cleanup
    with get_session() as session:
        session.delete(updated_task)


def test_edit_task_multiple_fields():
    """Test editing multiple fields at once."""
    task = create_task(title="Test Task")
    due = datetime.now() + timedelta(days=1)

    updated_task = edit_task(
        task.id,
        title="Updated Task",
        priority=Priority.HIGH,
        due_date=due,
        time_estimate_minutes=60
    )

    assert updated_task.title == "Updated Task"
    assert updated_task.priority == Priority.HIGH
    assert updated_task.due_date == due
    assert updated_task.time_estimate_minutes == 60

    # Cleanup
    with get_session() as session:
        session.delete(updated_task)


def test_edit_nonexistent_task():
    """Test editing a task that doesn't exist."""
    with pytest.raises(ValueError, match="Task with id 99999 not found"):
        edit_task(99999, title="New Title")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db_edit_task.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.db.functions.edit_task'"

**Step 3: Create the edit_task function**

Create `src/db/functions/edit_task.py`:
```python
"""Edit task database function."""
from datetime import datetime
from typing import Optional

from sqlmodel import select

from src.db.engine import get_session
from src.models import Task, Priority, RepeatInterval


def edit_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[Priority] = None,
    due_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    time_estimate_minutes: Optional[int] = None,
    repeat_interval: Optional[RepeatInterval] = None,
) -> Task:
    """
    Edit an existing task.

    Args:
        task_id: ID of the task to edit
        title: New title (if provided)
        description: New description (if provided)
        completed: New completion status (if provided)
        priority: New priority (if provided)
        due_date: New due date (if provided)
        start_date: New start date (if provided)
        time_estimate_minutes: New time estimate (if provided)
        repeat_interval: New repeat interval (if provided)

    Returns:
        Updated Task object

    Raises:
        ValueError: If task with given ID doesn't exist
    """
    with get_session() as session:
        statement = select(Task).where(Task.id == task_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        # Update fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed
            if completed:
                task.completed_at = datetime.now()
            else:
                task.completed_at = None
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        if start_date is not None:
            task.start_date = start_date
        if time_estimate_minutes is not None:
            task.time_estimate_minutes = time_estimate_minutes
        if repeat_interval is not None:
            task.repeat_interval = repeat_interval

        task.updated_at = datetime.now()

        session.add(task)
        session.commit()
        session.refresh(task)

    return task
```

**Step 4: Modify __init__.py to export new function**

Modify `src/db/functions/__init__.py`:
```python
"""Database CRUD functions."""
from src.db.functions.create_task import create_task
from src.db.functions.list_tasks import list_tasks
from src.db.functions.edit_task import edit_task

__all__ = ["create_task", "list_tasks", "edit_task"]
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_db_edit_task.py -v`
Expected: PASS (4 tests)

**Step 6: Commit**

Run:
```bash
git add src/db/functions/edit_task.py src/db/functions/__init__.py tests/test_db_edit_task.py
git commit -m "feat: add edit_task database function"
```

---

## Task 10: CRUD Functions - Delete Task

**Files:**
- Create: `src/db/functions/delete_task.py`
- Modify: `src/db/functions/__init__.py`
- Create: `tests/test_db_delete_task.py`

**Step 1: Write the failing test**

Create `tests/test_db_delete_task.py`:
```python
import pytest
from sqlmodel import select
from src.db.functions.create_task import create_task
from src.db.functions.delete_task import delete_task
from src.db.engine import get_session
from src.models import Task


def test_delete_existing_task():
    """Test deleting an existing task."""
    task = create_task(title="Task to Delete")
    task_id = task.id

    result = delete_task(task_id)

    assert result is True

    # Verify task is actually deleted
    with get_session() as session:
        statement = select(Task).where(Task.id == task_id)
        deleted_task = session.exec(statement).first()
        assert deleted_task is None


def test_delete_nonexistent_task():
    """Test deleting a task that doesn't exist."""
    result = delete_task(99999)

    assert result is False
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db_delete_task.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.db.functions.delete_task'"

**Step 3: Create the delete_task function**

Create `src/db/functions/delete_task.py`:
```python
"""Delete task database function."""
from sqlmodel import select

from src.db.engine import get_session
from src.models import Task


def delete_task(task_id: int) -> bool:
    """
    Delete a task from the database.

    Args:
        task_id: ID of the task to delete

    Returns:
        True if task was deleted, False if task didn't exist
    """
    with get_session() as session:
        statement = select(Task).where(Task.id == task_id)
        task = session.exec(statement).first()

        if not task:
            return False

        session.delete(task)
        session.commit()

    return True
```

**Step 4: Modify __init__.py to export new function**

Modify `src/db/functions/__init__.py`:
```python
"""Database CRUD functions."""
from src.db.functions.create_task import create_task
from src.db.functions.list_tasks import list_tasks
from src.db.functions.edit_task import edit_task
from src.db.functions.delete_task import delete_task

__all__ = ["create_task", "list_tasks", "edit_task", "delete_task"]
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_db_delete_task.py -v`
Expected: PASS (2 tests)

**Step 6: Commit**

Run:
```bash
git add src/db/functions/delete_task.py src/db/functions/__init__.py tests/test_db_delete_task.py
git commit -m "feat: add delete_task database function"
```

---

## Task 11: CRUD Functions - Create and Manage Tags

**Files:**
- Create: `src/db/functions/create_tag.py`
- Create: `src/db/functions/list_tags.py`
- Create: `src/db/functions/add_tag_to_task.py`
- Create: `src/db/functions/remove_tag_from_task.py`
- Modify: `src/db/functions/__init__.py`
- Create: `tests/test_db_tags.py`

**Step 1: Write the failing test**

Create `tests/test_db_tags.py`:
```python
import pytest
from src.db.functions.create_task import create_task
from src.db.functions.create_tag import create_tag
from src.db.functions.list_tags import list_tags
from src.db.functions.add_tag_to_task import add_tag_to_task
from src.db.functions.remove_tag_from_task import remove_tag_from_task
from src.db.engine import get_session


def test_create_tag():
    """Test creating a tag."""
    tag = create_tag(name="test-tag", color="#FF0000")

    assert tag.id is not None
    assert tag.name == "test-tag"
    assert tag.color == "#FF0000"

    # Cleanup
    with get_session() as session:
        session.delete(tag)


def test_list_tags():
    """Test listing all tags."""
    tag1 = create_tag(name="tag1", color="#FF0000")
    tag2 = create_tag(name="tag2", color="#00FF00")

    tags = list_tags()
    tag_names = [t.name for t in tags]

    assert "tag1" in tag_names
    assert "tag2" in tag_names

    # Cleanup
    with get_session() as session:
        session.delete(tag1)
        session.delete(tag2)


def test_add_tag_to_task():
    """Test adding a tag to a task."""
    task = create_task(title="Test Task")
    tag = create_tag(name="work-tag", color="#0000FF")

    updated_task = add_tag_to_task(task.id, tag.id)

    assert len(updated_task.tags) == 1
    assert updated_task.tags[0].name == "work-tag"

    # Cleanup
    with get_session() as session:
        session.delete(task)
        session.delete(tag)


def test_remove_tag_from_task():
    """Test removing a tag from a task."""
    task = create_task(title="Test Task")
    tag = create_tag(name="temp-tag", color="#FF00FF")

    # Add tag first
    task_with_tag = add_tag_to_task(task.id, tag.id)
    assert len(task_with_tag.tags) == 1

    # Remove tag
    task_without_tag = remove_tag_from_task(task.id, tag.id)
    assert len(task_without_tag.tags) == 0

    # Cleanup
    with get_session() as session:
        session.delete(task)
        session.delete(tag)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db_tags.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create the tag functions**

Create `src/db/functions/create_tag.py`:
```python
"""Create tag database function."""
from src.db.engine import get_session
from src.models import Tag


def create_tag(name: str, color: str = "#808080") -> Tag:
    """
    Create a new tag.

    Args:
        name: Tag name (must be unique)
        color: Hex color code (default gray)

    Returns:
        Created Tag object
    """
    tag = Tag(name=name, color=color)

    with get_session() as session:
        session.add(tag)
        session.commit()
        session.refresh(tag)

    return tag
```

Create `src/db/functions/list_tags.py`:
```python
"""List tags database function."""
from sqlmodel import select

from src.db.engine import get_session
from src.models import Tag


def list_tags() -> list[Tag]:
    """
    List all tags ordered by name.

    Returns:
        List of all Tag objects
    """
    with get_session() as session:
        statement = select(Tag).order_by(Tag.name)
        tags = session.exec(statement).all()

    return list(tags)
```

Create `src/db/functions/add_tag_to_task.py`:
```python
"""Add tag to task database function."""
from sqlmodel import select

from src.db.engine import get_session
from src.models import Task, Tag


def add_tag_to_task(task_id: int, tag_id: int) -> Task:
    """
    Add a tag to a task.

    Args:
        task_id: ID of the task
        tag_id: ID of the tag to add

    Returns:
        Updated Task object with tags loaded

    Raises:
        ValueError: If task or tag doesn't exist
    """
    with get_session() as session:
        task = session.exec(select(Task).where(Task.id == task_id)).first()
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
        if not tag:
            raise ValueError(f"Tag with id {tag_id} not found")

        if tag not in task.tags:
            task.tags.append(tag)
            session.add(task)
            session.commit()
            session.refresh(task)

    return task
```

Create `src/db/functions/remove_tag_from_task.py`:
```python
"""Remove tag from task database function."""
from sqlmodel import select

from src.db.engine import get_session
from src.models import Task, Tag


def remove_tag_from_task(task_id: int, tag_id: int) -> Task:
    """
    Remove a tag from a task.

    Args:
        task_id: ID of the task
        tag_id: ID of the tag to remove

    Returns:
        Updated Task object

    Raises:
        ValueError: If task or tag doesn't exist
    """
    with get_session() as session:
        task = session.exec(select(Task).where(Task.id == task_id)).first()
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
        if not tag:
            raise ValueError(f"Tag with id {tag_id} not found")

        if tag in task.tags:
            task.tags.remove(tag)
            session.add(task)
            session.commit()
            session.refresh(task)

    return task
```

**Step 4: Modify __init__.py to export new functions**

Modify `src/db/functions/__init__.py`:
```python
"""Database CRUD functions."""
from src.db.functions.create_task import create_task
from src.db.functions.list_tasks import list_tasks
from src.db.functions.edit_task import edit_task
from src.db.functions.delete_task import delete_task
from src.db.functions.create_tag import create_tag
from src.db.functions.list_tags import list_tags
from src.db.functions.add_tag_to_task import add_tag_to_task
from src.db.functions.remove_tag_from_task import remove_tag_from_task

__all__ = [
    "create_task",
    "list_tasks",
    "edit_task",
    "delete_task",
    "create_tag",
    "list_tags",
    "add_tag_to_task",
    "remove_tag_from_task",
]
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_db_tags.py -v`
Expected: PASS (4 tests)

**Step 6: Commit**

Run:
```bash
git add src/db/functions/ tests/test_db_tags.py
git commit -m "feat: add tag management functions"
```

---

## Task 12: Docker Compose Setup

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `.dockerignore`

**Step 1: Create docker-compose.yml**

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: todo-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-todo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-todo}
      POSTGRES_DB: ${POSTGRES_DB:-tododb}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-todo}"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    container_name: todo-app
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-todo}:${POSTGRES_PASSWORD:-todo}@postgres:5432/${POSTGRES_DB:-tododb}
      DATABASE_ECHO: ${DATABASE_ECHO:-false}
    ports:
      - "8501:8501"
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    command: >
      sh -c "
        uv run python -m src.db.init_db &&
        uv run python -m src.db.seed &&
        uv run streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
      "

volumes:
  postgres_data:
```

**Step 2: Create Dockerfile**

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml .python-version ./

# Install dependencies
RUN uv sync

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Expose Streamlit port
EXPOSE 8501

# Default command (overridden by docker-compose)
CMD ["uv", "run", "streamlit", "run", "src/app.py"]
```

**Step 3: Create .dockerignore**

Create `.dockerignore`:
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
.pytest_cache/
.ruff_cache/
.env
.env.local
.git/
.gitignore
.DS_Store
*.md
docs/
postgres_data/
```

**Step 4: Test Docker setup**

Run: `docker-compose config`
Expected: Valid YAML configuration output

**Step 5: Commit**

Run:
```bash
git add docker-compose.yml Dockerfile .dockerignore
git commit -m "feat: add Docker Compose setup with PostgreSQL"
```

---

## Task 13: Streamlit UI - Basic Layout and Task List

**Files:**
- Create: `src/app.py`

**Step 1: Create basic Streamlit app**

Create `src/app.py`:
```python
"""Streamlit TODO application."""
import streamlit as st
from datetime import datetime

from src.db.functions import list_tasks, create_task, edit_task, delete_task
from src.db.functions import list_tags, add_tag_to_task, remove_tag_from_task
from src.models import Priority, RepeatInterval

# Page config
st.set_page_config(
    page_title="TODO App",
    page_icon="✓",
    layout="wide",
)

st.title("✓ TODO App")

# Sidebar for filters
st.sidebar.header("Filters")
show_completed = st.sidebar.checkbox("Show completed tasks", value=False)
priority_filter = st.sidebar.selectbox(
    "Filter by priority",
    options=[None, Priority.HIGH, Priority.MEDIUM, Priority.LOW],
    format_func=lambda x: "All priorities" if x is None else x.value.title(),
)

# Main section - Create new task
st.header("Create New Task")

with st.form("new_task_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])

    with col1:
        new_title = st.text_input("Title", placeholder="Enter task title...")

    with col2:
        new_priority = st.selectbox(
            "Priority",
            options=[Priority.HIGH, Priority.MEDIUM, Priority.LOW],
            format_func=lambda x: x.value.title(),
        )

    new_description = st.text_area("Description", placeholder="Task description (optional)")

    col3, col4, col5 = st.columns(3)

    with col3:
        new_due_date = st.date_input("Due date", value=None)

    with col4:
        new_time_estimate = st.selectbox(
            "Time estimate",
            options=[None, 5, 15, 30, 60, 120, 240],
            format_func=lambda x: "No estimate" if x is None else f"{x} minutes",
        )

    with col5:
        new_repeat = st.selectbox(
            "Repeat",
            options=[None, RepeatInterval.HOURLY, RepeatInterval.DAILY,
                    RepeatInterval.WEEKLY, RepeatInterval.MONTHLY],
            format_func=lambda x: "No repeat" if x is None else x.value.title(),
        )

    submit_button = st.form_submit_button("Add Task", use_container_width=True)

    if submit_button and new_title:
        try:
            create_task(
                title=new_title,
                description=new_description if new_description else None,
                priority=new_priority,
                due_date=datetime.combine(new_due_date, datetime.min.time()) if new_due_date else None,
                time_estimate_minutes=new_time_estimate,
                repeat_interval=new_repeat,
            )
            st.success(f"Task '{new_title}' created successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error creating task: {e}")

# Task list section
st.header("Tasks")

# Fetch tasks with filters
tasks = list_tasks(
    completed=show_completed if show_completed else False,
    priority=priority_filter,
)

if not tasks:
    st.info("No tasks found. Create one above!")
else:
    for task in tasks:
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 4, 2, 1])

            with col1:
                # Checkbox to mark complete
                is_completed = st.checkbox(
                    "Done",
                    value=task.completed,
                    key=f"complete_{task.id}",
                    label_visibility="collapsed",
                )
                if is_completed != task.completed:
                    edit_task(task.id, completed=is_completed)
                    st.rerun()

            with col2:
                # Task title and description
                st.markdown(f"**{task.title}**")
                if task.description:
                    st.caption(task.description)

            with col3:
                # Priority badge
                priority_colors = {
                    Priority.HIGH: "🔴",
                    Priority.MEDIUM: "🟡",
                    Priority.LOW: "🟢",
                }
                st.text(f"{priority_colors[task.priority]} {task.priority.value.title()}")

                # Due date if set
                if task.due_date:
                    st.caption(f"Due: {task.due_date.strftime('%Y-%m-%d')}")

            with col4:
                # Delete button
                if st.button("Delete", key=f"delete_{task.id}"):
                    delete_task(task.id)
                    st.success(f"Task deleted!")
                    st.rerun()

            st.divider()

# Footer
st.sidebar.divider()
st.sidebar.caption(f"Total tasks: {len(tasks)}")
```

**Step 2: Test the app locally (requires running PostgreSQL)**

Run: `uv run streamlit run src/app.py`
Expected: Streamlit app opens in browser

**Step 3: Commit**

Run:
```bash
git add src/app.py
git commit -m "feat: add basic Streamlit UI with task list and creation"
```

---

## Task 14: Run Complete Test Suite

**Files:**
- N/A (running existing tests)

**Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass

**Step 2: Check code quality with ruff**

Run: `uvx ruff check src/ tests/`
Expected: No errors

**Step 3: Format code with ruff**

Run: `uvx ruff format src/ tests/`
Expected: Code formatted

**Step 4: Commit any formatting changes**

Run:
```bash
git add src/ tests/
git commit -m "style: format code with ruff"
```

---

## Task 15: Create README with Usage Instructions

**Files:**
- Create: `README.md`

**Step 1: Create comprehensive README**

Create `README.md`:
```markdown
# TODO Application

A personal TODO application with Streamlit UI, PostgreSQL database, and comprehensive task management features.

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

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) uv for local development

### Run with Docker Compose

1. Clone the repository
2. Start the application:

```bash
docker-compose up --build
```

3. Access the app at `http://localhost:8501`

The PostgreSQL database will automatically initialize with tables and seed data.

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

## Project Structure

```
.
├── src/
│   ├── app.py              # Streamlit UI
│   ├── settings.py          # Configuration with pydantic-settings
│   ├── models.py            # SQLModel database models
│   ├── db/
│   │   ├── engine.py        # Database engine and session
│   │   ├── init_db.py       # Database initialization
│   │   ├── seed.py          # Database seeding
│   │   └── functions/       # CRUD operations
│   │       ├── create_task.py
│   │       ├── list_tasks.py
│   │       ├── edit_task.py
│   │       ├── delete_task.py
│   │       ├── create_tag.py
│   │       └── ...
│   └── services/            # Business logic (future)
├── tests/                   # pytest test suite
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Application container
└── pyproject.toml          # Project dependencies

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

## License

MIT
```

**Step 2: Commit**

Run:
```bash
git add README.md
git commit -m "docs: add comprehensive README"
```

---

## Task 16: Final Integration Test

**Files:**
- N/A (integration testing)

**Step 1: Stop any running containers**

Run: `docker-compose down -v`
Expected: All containers stopped and volumes removed

**Step 2: Build and start fresh**

Run: `docker-compose up --build`
Expected:
- PostgreSQL starts and becomes healthy
- Database tables are created
- Initial tags are seeded
- Streamlit app starts on port 8501

**Step 3: Verify the application**

Open browser to `http://localhost:8501` and verify:
- App loads successfully
- Can create a new task
- Can mark task as complete
- Can delete a task
- Filters work correctly

**Step 4: Stop containers**

Run: `docker-compose down`

**Step 5: Final commit**

Run:
```bash
git add -A
git commit -m "chore: final integration test complete"
```

---

## Summary

This plan provides a complete implementation of the TODO application with:

1. ✅ Project setup with uv and dependencies
2. ✅ Configuration management with pydantic-settings
3. ✅ Database models with SQLModel
4. ✅ Database engine and session management
5. ✅ Database initialization and seeding
6. ✅ Complete CRUD operations for tasks
7. ✅ Tag management functionality
8. ✅ Docker Compose orchestration
9. ✅ Streamlit UI with all features
10. ✅ Comprehensive test suite
11. ✅ Documentation

Each task follows TDD principles with test-first development, frequent commits, and verification steps.
