import pytest
from datetime import datetime, timedelta
from sqlmodel import select
from src.db.functions.create_task import create_task
from src.db.functions.list_tasks import list_tasks
from src.db.engine import get_session
from src.models import Task, Priority


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    task1 = create_task(title="Task 1", priority=Priority.HIGH)
    task2 = create_task(title="Task 2", priority=Priority.LOW)
    task3 = create_task(title="Task 3", priority=Priority.MEDIUM)

    # Mark task2 as completed manually
    with get_session() as session:
        db_task2 = session.exec(select(Task).where(Task.id == task2.id)).first()
        if db_task2:
            db_task2.completed = True
            session.add(db_task2)
            session.commit()

    tasks = [task1, task2, task3]
    yield tasks

    # Cleanup
    with get_session() as session:
        for task in tasks:
            db_task = session.exec(select(Task).where(Task.id == task.id)).first()
            if db_task:
                session.delete(db_task)


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
