"""Create tag database function."""

from src.db.engine import get_session
from src.models import Tag


def create_tag(name: str, color: str = "#808080") -> Tag:
    """Create a new tag.

    Args:
        name: Tag name (must be unique)
        color: Hex color code (default gray)

    Returns:
        Created Tag object
    """
    tag = Tag(name=name, color=color)

    with get_session() as session:
        session.add(tag)
        session.commit()
        session.refresh(tag)

        # Convert to detached instance
        tag_data = {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
        }

    return Tag(**tag_data)
