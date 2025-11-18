"""LangChain tool wrappers for database functions."""

from datetime import datetime

from langchain_core.tools import tool

from src.db.functions import (
    add_tag_to_task,
    create_tag,
    create_task,
    delete_task,
    edit_task,
    list_tags,
    list_tasks,
    remove_tag_from_task,
)
from src.models import Priority, RepeatInterval, Tag, Task


def parse_priority(value: str) -> Priority:
    """Parse priority string to Priority enum.

    Args:
        value: Priority string (case-insensitive)

    Returns:
        Priority enum value

    Raises:
        ValueError: If value is not a valid priority
    """
    try:
        return Priority(value.lower())
    except ValueError:
        valid_options = ", ".join([p.value for p in Priority])
        raise ValueError(f"Invalid priority '{value}'. Valid options: {valid_options}")


def parse_repeat_interval(value: str) -> RepeatInterval:
    """Parse repeat interval string to RepeatInterval enum.

    Args:
        value: Repeat interval string (case-insensitive)

    Returns:
        RepeatInterval enum value

    Raises:
        ValueError: If value is not a valid repeat interval
    """
    try:
        return RepeatInterval(value.lower())
    except ValueError:
        valid_options = ", ".join([r.value for r in RepeatInterval])
        raise ValueError(
            f"Invalid repeat interval '{value}'. Valid options: {valid_options}"
        )


def parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetime string to datetime object.

    Args:
        value: ISO datetime string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) or None

    Returns:
        datetime object or None if value is None

    Raises:
        ValueError: If value is not a valid ISO datetime format
    """
    if value is None:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"Invalid datetime '{value}'. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
        )


# Tool Wrappers


@tool
def create_task_tool(
    title: str,
    description: str | None = None,
    priority: str = "medium",
    due_date: str | None = None,
    start_date: str | None = None,
    time_estimate_minutes: int | None = None,
    repeat_interval: str | None = None,
) -> Task:
    """Create a new task in the todo list.

    Args:
        title: Task title (required)
        description: Optional task description
        priority: Priority level - must be 'low', 'medium', or 'high'
        due_date: Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        start_date: Start date in ISO format
        time_estimate_minutes: Estimated completion time in minutes
        repeat_interval: How often task repeats - 'hourly', 'daily', 'weekly', or 'monthly'

    Returns:
        Created Task object with assigned ID
    """
    return create_task(
        title=title,
        description=description,
        priority=parse_priority(priority),
        due_date=parse_datetime(due_date),
        start_date=parse_datetime(start_date),
        time_estimate_minutes=time_estimate_minutes,
        repeat_interval=parse_repeat_interval(repeat_interval)
        if repeat_interval
        else None,
    )


@tool
def list_tasks_tool(
    completed: bool | None = None,
    priority: str | None = None,
) -> list[Task]:
    """List tasks with optional filters.

    Args:
        completed: Filter by completion status - true for completed, false for incomplete, omit for all
        priority: Filter by priority - 'low', 'medium', or 'high', omit for all

    Returns:
        List of Task objects matching the filters, ordered by completion status, due date, and priority
    """
    priority_enum = parse_priority(priority) if priority else None
    return list_tasks(completed=completed, priority=priority_enum)


@tool
def edit_task_tool(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
    priority: str | None = None,
    due_date: str | None = None,
    start_date: str | None = None,
    time_estimate_minutes: int | None = None,
    repeat_interval: str | None = None,
) -> Task:
    """Edit an existing task. Only provided fields will be updated.

    Args:
        task_id: ID of the task to edit (required)
        title: New task title
        description: New description
        completed: New completion status
        priority: New priority - 'low', 'medium', or 'high'
        due_date: New due date in ISO format
        start_date: New start date in ISO format
        time_estimate_minutes: New time estimate in minutes
        repeat_interval: New repeat interval - 'hourly', 'daily', 'weekly', or 'monthly'

    Returns:
        Updated Task object

    Raises:
        ValueError: If task with given ID doesn't exist
    """
    return edit_task(
        task_id=task_id,
        title=title,
        description=description,
        completed=completed,
        priority=parse_priority(priority) if priority else None,
        due_date=parse_datetime(due_date),
        start_date=parse_datetime(start_date),
        time_estimate_minutes=time_estimate_minutes,
        repeat_interval=parse_repeat_interval(repeat_interval)
        if repeat_interval
        else None,
    )


@tool
def delete_task_tool(task_id: int) -> bool:
    """Delete a task from the database.

    Args:
        task_id: ID of the task to delete

    Returns:
        True if task was deleted, False if task didn't exist
    """
    return delete_task(task_id=task_id)


@tool
def create_tag_tool(name: str, color: str = "#808080") -> Tag:
    """Create a new tag for categorizing tasks.

    Args:
        name: Tag name (required, must be unique)
        color: Hex color code (e.g., '#FF5733'), defaults to gray

    Returns:
        Created Tag object with assigned ID
    """
    return create_tag(name=name, color=color)


@tool
def list_tags_tool() -> list[Tag]:
    """List all available tags.

    Returns:
        List of all Tag objects
    """
    return list_tags()


@tool
def add_tag_to_task_tool(task_id: int, tag_id: int) -> Task:
    """Add a tag to a task.

    Args:
        task_id: ID of the task
        tag_id: ID of the tag to add

    Returns:
        Updated Task object with tags loaded

    Raises:
        ValueError: If task or tag doesn't exist
    """
    return add_tag_to_task(task_id=task_id, tag_id=tag_id)


@tool
def remove_tag_from_task_tool(task_id: int, tag_id: int) -> Task:
    """Remove a tag from a task.

    Args:
        task_id: ID of the task
        tag_id: ID of the tag to remove

    Returns:
        Updated Task object with tags loaded

    Raises:
        ValueError: If task or tag doesn't exist
    """
    return remove_tag_from_task(task_id=task_id, tag_id=tag_id)


# Export all tools as a list for LangGraph
TOOLS = [
    create_task_tool,
    list_tasks_tool,
    edit_task_tool,
    delete_task_tool,
    create_tag_tool,
    list_tags_tool,
    add_tag_to_task_tool,
    remove_tag_from_task_tool,
]
