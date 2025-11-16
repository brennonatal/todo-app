from src.settings import Settings


def test_settings_loads_from_env(monkeypatch):
    """Test that settings load from environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
    monkeypatch.setenv("DATABASE_ECHO", "true")

    settings = Settings()

    assert settings.database_url == "postgresql://test:test@localhost:5432/testdb"
    assert settings.database_echo is True


def test_settings_has_defaults():
    """Test that settings have reasonable defaults."""
    settings = Settings()

    assert settings.app_name == "TODO App"
    assert settings.database_echo is False
