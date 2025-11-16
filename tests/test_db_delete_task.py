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
