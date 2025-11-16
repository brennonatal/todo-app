import pytest
from sqlalchemy.exc import OperationalError
from sqlmodel import Field, Session, SQLModel, select

from src.db.engine import get_engine, get_session


class DbTestModel(SQLModel, table=True):
    """Test model for database operations."""

    __tablename__ = "test_table"

    id: int | None = Field(default=None, primary_key=True)
    name: str


def is_database_available():
    """Check if database is available for testing."""
    try:
        engine = get_engine()
        with engine.connect():
            return True
    except OperationalError:
        return False


# Mark tests that require database
requires_db = pytest.mark.skipif(
    not is_database_available(), reason="Database not available"
)


def test_get_engine():
    """Test that get_engine returns a valid engine."""
    engine = get_engine()

    assert engine is not None
    assert hasattr(engine, "url")


def test_get_engine_singleton():
    """Test that get_engine returns the same engine instance."""
    engine1 = get_engine()
    engine2 = get_engine()

    assert engine1 is engine2, "get_engine should return the same instance"


def test_get_session():
    """Test that get_session returns a valid session."""
    with get_session() as session:
        assert isinstance(session, Session)
        assert session.bind is not None


@requires_db
def test_session_auto_commit():
    """Test that session automatically commits on success."""
    # Create table for testing
    SQLModel.metadata.create_all(get_engine())

    # Create a record in the session
    with get_session() as session:
        test_record = DbTestModel(name="test_commit")
        session.add(test_record)
        # Commit happens automatically when exiting context

    # Verify the record was committed by reading it in a new session
    with get_session() as session:
        statement = select(DbTestModel).where(DbTestModel.name == "test_commit")
        result = session.exec(statement).first()
        assert result is not None, "Record should be committed automatically"
        assert result.name == "test_commit"

    # Cleanup
    with get_session() as session:
        statement = select(DbTestModel).where(DbTestModel.name == "test_commit")
        records = session.exec(statement).all()
        for record in records:
            session.delete(record)


@requires_db
def test_session_rollback_on_exception():
    """Test that session rolls back on exceptions."""
    # Create table for testing
    SQLModel.metadata.create_all(get_engine())

    # Try to create a record but raise an exception
    with pytest.raises(ValueError):
        with get_session() as session:
            test_record = DbTestModel(name="test_rollback")
            session.add(test_record)
            session.flush()  # Write to DB but don't commit yet
            raise ValueError("Test exception")

    # Verify the record was NOT committed due to rollback
    with get_session() as session:
        statement = select(DbTestModel).where(DbTestModel.name == "test_rollback")
        result = session.exec(statement).first()
        assert result is None, "Record should be rolled back on exception"
