"""Create task database function."""

from datetime import datetime

from src.db.engine import get_session
from src.models import Priority, RepeatInterval, Task


def create_task(
    title: str,
    description: str | None = None,
    priority: Priority = Priority.MEDIUM,
    due_date: datetime | None = None,
    start_date: datetime | None = None,
    time_estimate_minutes: int | None = None,
    repeat_interval: RepeatInterval | None = None,
) -> Task:
    """Create a new task in the database.

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

        # Access attributes while session is still open to avoid DetachedInstanceError
        task_id = task.id
        task_data = {
            "id": task_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "due_date": task.due_date,
            "start_date": task.start_date,
            "completed_at": task.completed_at,
            "time_estimate_minutes": task.time_estimate_minutes,
            "repeat_interval": task.repeat_interval,
        }

    # Create a new detached instance with the same data
    return Task(**task_data)
