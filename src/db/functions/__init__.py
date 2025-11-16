"""Database CRUD functions."""
from src.db.functions.create_task import create_task
from src.db.functions.list_tasks import list_tasks
from src.db.functions.edit_task import edit_task
from src.db.functions.delete_task import delete_task
from src.db.functions.create_tag import create_tag
from src.db.functions.list_tags import list_tags
from src.db.functions.add_tag_to_task import add_tag_to_task
from src.db.functions.remove_tag_from_task import remove_tag_from_task

__all__ = [
    "create_task",
    "list_tasks",
    "edit_task",
    "delete_task",
    "create_tag",
    "list_tags",
    "add_tag_to_task",
    "remove_tag_from_task",
]
