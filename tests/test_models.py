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
