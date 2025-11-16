"""Add tag to task database function."""

from sqlmodel import select

from src.db.engine import get_session
from src.models import Tag, Task


def add_tag_to_task(task_id: int, tag_id: int) -> Task:
    """Add a tag to a task.

    Args:
        task_id: ID of the task
        tag_id: ID of the tag to add

    Returns:
        Updated Task object with tags loaded

    Raises:
        ValueError: If task or tag doesn't exist
    """
    with get_session() as session:
        task = session.exec(select(Task).where(Task.id == task_id)).first()
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
        if not tag:
            raise ValueError(f"Tag with id {tag_id} not found")

        if tag not in task.tags:
            task.tags.append(tag)
            session.add(task)
            session.commit()
            session.refresh(task)

        # Convert to detached instance with tags
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

        # Create detached task
        detached_task = Task(**task_data)

        # Convert tags to detached instances
        detached_tags = []
        for t in task.tags:
            tag_data = {
                "id": t.id,
                "name": t.name,
                "color": t.color,
            }
            detached_tags.append(Tag(**tag_data))

        detached_task.tags = detached_tags

    return detached_task
