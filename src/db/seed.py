"""Database seeding script - creates initial tags."""

from sqlmodel import select

from src.db.engine import get_session
from src.models import Tag


def seed_initial_tags() -> None:
    """Create initial tags if they don't exist."""
    initial_tags = [
        Tag(name="work", color="#3B82F6"),  # Blue
        Tag(name="personal", color="#10B981"),  # Green
        Tag(name="urgent", color="#EF4444"),  # Red
        Tag(name="learning", color="#8B5CF6"),  # Purple
        Tag(name="health", color="#F59E0B"),  # Orange
    ]

    with get_session() as session:
        for tag_data in initial_tags:
            # Check if tag already exists
            statement = select(Tag).where(Tag.name == tag_data.name)
            existing_tag = session.exec(statement).first()

            if not existing_tag:
                session.add(tag_data)
                print(f"Created tag: {tag_data.name}")  # noqa: T201
            else:
                print(f"Tag already exists: {tag_data.name}")  # noqa: T201

        session.commit()

    print("Database seeding completed")  # noqa: T201


if __name__ == "__main__":
    seed_initial_tags()
