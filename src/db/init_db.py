"""Database initialization script - creates all tables."""

from sqlmodel import SQLModel

from src.db.engine import get_engine
from src.models import Tag, Task, TaskTagLink  # noqa: F401 - needed for table creation


def init_db() -> None:
    """Initialize database by creating all tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")


if __name__ == "__main__":
    init_db()
