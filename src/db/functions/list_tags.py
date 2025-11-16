"""List tags database function."""

from sqlmodel import select

from src.db.engine import get_session
from src.models import Tag


def list_tags() -> list[Tag]:
    """List all tags ordered by name.

    Returns:
        List of all Tag objects
    """
    with get_session() as session:
        statement = select(Tag).order_by(Tag.name)
        tags = session.exec(statement).all()

        # Convert to list of detached Tag objects
        result = []
        for tag in tags:
            tag_data = {
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
            }
            result.append(Tag(**tag_data))

    return result
