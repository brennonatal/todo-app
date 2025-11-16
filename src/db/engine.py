"""Database engine and session management."""
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, create_engine

from src.settings import settings


def get_engine():
    """Create and return database engine."""
    return create_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,  # Verify connections before using
    )


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
