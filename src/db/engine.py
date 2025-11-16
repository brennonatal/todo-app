"""Database engine and session management."""

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, create_engine

from src.settings import settings

# Module-level engine singleton
_engine = None


def get_engine():
    """Get or create the database engine singleton.

    This ensures connection pooling works properly by reusing
    the same engine across all database sessions.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_pre_ping=True,  # Verify connections before using
        )
    return _engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions.

    Automatically commits on success and rolls back on exceptions.
    Always closes the session properly.
    """
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
