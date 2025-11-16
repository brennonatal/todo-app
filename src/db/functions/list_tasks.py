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

        # Convert to list of detached Task objects
        result = []
        for task in tasks:
            task_data = {
                "id": task.id,
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
            result.append(Task(**task_data))

    return result
