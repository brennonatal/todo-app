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

        # Convert to detached instance
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

    return Task(**task_data)
