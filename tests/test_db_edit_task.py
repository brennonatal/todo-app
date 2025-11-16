import pytest
from datetime import datetime, timedelta
from sqlmodel import select
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
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)


def test_edit_task_completion():
    """Test marking a task as completed."""
    task = create_task(title="Test Task")

    updated_task = edit_task(task.id, completed=True)

    assert updated_task.completed is True
    assert updated_task.completed_at is not None

    # Cleanup
    with get_session() as session:
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)


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
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)


def test_edit_nonexistent_task():
    """Test editing a task that doesn't exist."""
    with pytest.raises(ValueError, match="Task with id 99999 not found"):
        edit_task(99999, title="New Title")
