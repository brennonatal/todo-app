import pytest
from datetime import datetime, timedelta
from sqlmodel import select
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
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)


def test_create_task_with_priority():
    """Test creating a task with priority."""
    task = create_task(
        title="High Priority Task",
        priority=Priority.HIGH
    )

    assert task.priority == Priority.HIGH

    # Cleanup
    with get_session() as session:
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)


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
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)
