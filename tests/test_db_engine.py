import pytest
from sqlmodel import Session
from src.db.engine import get_engine, get_session


def test_get_engine():
    """Test that get_engine returns a valid engine."""
    engine = get_engine()

    assert engine is not None
    assert hasattr(engine, "url")


def test_get_session():
    """Test that get_session returns a valid session."""
    with get_session() as session:
        assert isinstance(session, Session)
        assert session.bind is not None
