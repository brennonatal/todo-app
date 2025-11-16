"""Database models using SQLModel."""

from datetime import datetime
from enum import Enum

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

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=50)
    color: str = Field(max_length=7, default="#808080")  # Hex color

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)


class Task(SQLModel, table=True):
    """Task model with all TODO features."""

    __tablename__ = "task"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False, index=True)

    # Priority
    priority: Priority = Field(default=Priority.MEDIUM, index=True)

    # Dates
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    due_date: datetime | None = Field(default=None, index=True)
    start_date: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    # Time estimate in minutes
    time_estimate_minutes: int | None = Field(default=None)

    # Repeat functionality
    repeat_interval: RepeatInterval | None = Field(default=None)

    # Relationships
    tags: list[Tag] = Relationship(back_populates="tasks", link_model=TaskTagLink)
