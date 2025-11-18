import os

from src.agent.config import Config


def test_config_init() -> None:
    config = Config(model="openai/gpt-4o-mini")
    assert config.model == "openai/gpt-4o-mini"


def test_config_init_with_env_vars() -> None:
    os.environ["MODEL"] = "openai/gpt-4o-mini"
    config = Config()
    assert config.model == "openai/gpt-4o-mini"


def test_config_init_with_env_vars_and_passed_values() -> None:
    os.environ["MODEL"] = "openai/gpt-4o-mini"
    config = Config(model="openai/gpt-5o-mini")
    assert config.model == "openai/gpt-5o-mini"
