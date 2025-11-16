import pytest
from sqlmodel import select
from src.db.functions.create_task import create_task
from src.db.functions.create_tag import create_tag
from src.db.functions.list_tags import list_tags
from src.db.functions.add_tag_to_task import add_tag_to_task
from src.db.functions.remove_tag_from_task import remove_tag_from_task
from src.db.engine import get_session
from src.models import Task, Tag


def test_create_tag():
    """Test creating a tag."""
    tag = create_tag(name="test-tag", color="#FF0000")

    assert tag.id is not None
    assert tag.name == "test-tag"
    assert tag.color == "#FF0000"

    # Cleanup
    with get_session() as session:
        db_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        if db_tag:
            session.delete(db_tag)


def test_list_tags():
    """Test listing all tags."""
    tag1 = create_tag(name="tag1", color="#FF0000")
    tag2 = create_tag(name="tag2", color="#00FF00")

    tags = list_tags()
    tag_names = [t.name for t in tags]

    assert "tag1" in tag_names
    assert "tag2" in tag_names

    # Cleanup
    with get_session() as session:
        db_tag1 = session.exec(select(Tag).where(Tag.id == tag1.id)).first()
        if db_tag1:
            session.delete(db_tag1)
        db_tag2 = session.exec(select(Tag).where(Tag.id == tag2.id)).first()
        if db_tag2:
            session.delete(db_tag2)


def test_add_tag_to_task():
    """Test adding a tag to a task."""
    task = create_task(title="Test Task")
    tag = create_tag(name="work-tag", color="#0000FF")

    updated_task = add_tag_to_task(task.id, tag.id)

    assert len(updated_task.tags) == 1
    assert updated_task.tags[0].name == "work-tag"

    # Cleanup
    with get_session() as session:
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)
        db_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        if db_tag:
            session.delete(db_tag)


def test_remove_tag_from_task():
    """Test removing a tag from a task."""
    task = create_task(title="Test Task")
    tag = create_tag(name="temp-tag", color="#FF00FF")

    # Add tag first
    task_with_tag = add_tag_to_task(task.id, tag.id)
    assert len(task_with_tag.tags) == 1

    # Remove tag
    task_without_tag = remove_tag_from_task(task.id, tag.id)
    assert len(task_without_tag.tags) == 0

    # Cleanup
    with get_session() as session:
        db_task = session.exec(select(Task).where(Task.id == task.id)).first()
        if db_task:
            session.delete(db_task)
        db_tag = session.exec(select(Tag).where(Tag.id == tag.id)).first()
        if db_tag:
            session.delete(db_tag)
