"""Delete task database function."""

from sqlmodel import select

from src.db.engine import get_session
from src.models import Task


def delete_task(task_id: int) -> bool:
    """Delete a task from the database.

    Args:
        task_id: ID of the task to delete

    Returns:
        True if task was deleted, False if task didn't exist
    """
    with get_session() as session:
        statement = select(Task).where(Task.id == task_id)
        task = session.exec(statement).first()

        if not task:
            return False

        session.delete(task)
        session.commit()

    return True
