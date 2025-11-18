"""Unit tests for agent tools and helper functions."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.agent.tools import (
    create_task_tool,
    list_tasks_tool,
    parse_datetime,
    parse_priority,
    parse_repeat_interval,
)
from src.models import Priority, RepeatInterval, Task


class TestParsePriority:
    """Tests for parse_priority helper function."""

    def test_parse_priority_low(self) -> None:
        """Test parsing 'low' priority."""
        result = parse_priority("low")
        assert result == Priority.LOW

    def test_parse_priority_medium(self) -> None:
        """Test parsing 'medium' priority."""
        result = parse_priority("medium")
        assert result == Priority.MEDIUM

    def test_parse_priority_high(self) -> None:
        """Test parsing 'high' priority."""
        result = parse_priority("high")
        assert result == Priority.HIGH

    def test_parse_priority_case_insensitive(self) -> None:
        """Test parsing is case-insensitive."""
        assert parse_priority("LOW") == Priority.LOW
        assert parse_priority("Medium") == Priority.MEDIUM
        assert parse_priority("HIGH") == Priority.HIGH

    def test_parse_priority_invalid_raises_error(self) -> None:
        """Test invalid priority raises ValueError with valid options."""
        with pytest.raises(ValueError) as exc_info:
            parse_priority("urgent")

        error_message = str(exc_info.value)
        assert "urgent" in error_message
        assert "low" in error_message
        assert "medium" in error_message
        assert "high" in error_message


class TestParseRepeatInterval:
    """Tests for parse_repeat_interval helper function."""

    def test_parse_repeat_interval_hourly(self) -> None:
        """Test parsing 'hourly' interval."""
        result = parse_repeat_interval("hourly")
        assert result == RepeatInterval.HOURLY

    def test_parse_repeat_interval_daily(self) -> None:
        """Test parsing 'daily' interval."""
        result = parse_repeat_interval("daily")
        assert result == RepeatInterval.DAILY

    def test_parse_repeat_interval_weekly(self) -> None:
        """Test parsing 'weekly' interval."""
        result = parse_repeat_interval("weekly")
        assert result == RepeatInterval.WEEKLY

    def test_parse_repeat_interval_monthly(self) -> None:
        """Test parsing 'monthly' interval."""
        result = parse_repeat_interval("monthly")
        assert result == RepeatInterval.MONTHLY

    def test_parse_repeat_interval_case_insensitive(self) -> None:
        """Test parsing is case-insensitive."""
        assert parse_repeat_interval("HOURLY") == RepeatInterval.HOURLY
        assert parse_repeat_interval("Daily") == RepeatInterval.DAILY
        assert parse_repeat_interval("WEEKLY") == RepeatInterval.WEEKLY

    def test_parse_repeat_interval_invalid_raises_error(self) -> None:
        """Test invalid interval raises ValueError with valid options."""
        with pytest.raises(ValueError) as exc_info:
            parse_repeat_interval("yearly")

        error_message = str(exc_info.value)
        assert "yearly" in error_message
        assert "hourly" in error_message
        assert "daily" in error_message
        assert "weekly" in error_message
        assert "monthly" in error_message


class TestParseDatetime:
    """Tests for parse_datetime helper function."""

    def test_parse_datetime_with_date_only(self) -> None:
        """Test parsing ISO date string (YYYY-MM-DD)."""
        result = parse_datetime("2024-12-01")
        assert result == datetime(2024, 12, 1, 0, 0, 0)

    def test_parse_datetime_with_date_and_time(self) -> None:
        """Test parsing ISO datetime string (YYYY-MM-DDTHH:MM:SS)."""
        result = parse_datetime("2024-12-01T14:30:00")
        assert result == datetime(2024, 12, 1, 14, 30, 0)

    def test_parse_datetime_with_none_returns_none(self) -> None:
        """Test parsing None returns None."""
        result = parse_datetime(None)
        assert result is None

    def test_parse_datetime_with_empty_string_returns_none(self) -> None:
        """Test parsing empty string returns None."""
        result = parse_datetime("")
        assert result is None

    def test_parse_datetime_invalid_format_raises_error(self) -> None:
        """Test invalid datetime format raises ValueError with format example."""
        with pytest.raises(ValueError) as exc_info:
            parse_datetime("tomorrow")

        error_message = str(exc_info.value)
        assert "tomorrow" in error_message
        assert "ISO" in error_message or "YYYY-MM-DD" in error_message


class TestCreateTaskTool:
    """Tests for create_task_tool wrapper."""

    @patch("src.agent.tools.create_task")
    def test_create_task_tool_with_minimal_params(
        self, mock_create_task: MagicMock
    ) -> None:
        """Test creating task with only required title parameter."""
        mock_task = Task(
            id=1,
            title="Test task",
            description=None,
            priority=Priority.MEDIUM,
        )
        mock_create_task.return_value = mock_task

        result = create_task_tool.invoke({"title": "Test task"})

        mock_create_task.assert_called_once_with(
            title="Test task",
            description=None,
            priority="medium",
            due_date=None,
            start_date=None,
            time_estimate_minutes=None,
            repeat_interval=None,
        )
        assert result == mock_task

    @patch("src.agent.tools.create_task")
    def test_create_task_tool_with_all_params(
        self, mock_create_task: MagicMock
    ) -> None:
        """Test creating task with all parameters."""
        mock_task = Task(
            id=1,
            title="Test task",
            description="Test description",
            priority=Priority.HIGH,
        )
        mock_create_task.return_value = mock_task

        result = create_task_tool.invoke(
            {
                "title": "Test task",
                "description": "Test description",
                "priority": "high",
                "due_date": "2024-12-01T14:30:00",
                "start_date": "2024-11-20",
                "time_estimate_minutes": 60,
                "repeat_interval": "daily",
            }
        )

        mock_create_task.assert_called_once_with(
            title="Test task",
            description="Test description",
            priority=Priority.HIGH,
            due_date=datetime(2024, 12, 1, 14, 30, 0),
            start_date=datetime(2024, 11, 20, 0, 0, 0),
            time_estimate_minutes=60,
            repeat_interval=RepeatInterval.DAILY,
        )
        assert result == mock_task

    @patch("src.agent.tools.create_task")
    def test_create_task_tool_converts_priority_string(
        self, mock_create_task: MagicMock
    ) -> None:
        """Test tool converts priority string to enum."""
        mock_task = Task(id=1, title="Test", priority=Priority.LOW)
        mock_create_task.return_value = mock_task

        create_task_tool.invoke({"title": "Test", "priority": "low"})

        call_args = mock_create_task.call_args
        assert call_args[1]["priority"] == Priority.LOW


class TestListTasksTool:
    """Tests for list_tasks_tool wrapper."""

    @patch("src.agent.tools.list_tasks")
    def test_list_tasks_tool_no_filters(self, mock_list_tasks: MagicMock) -> None:
        """Test listing tasks without filters."""
        mock_tasks = [
            Task(id=1, title="Task 1", priority=Priority.HIGH),
            Task(id=2, title="Task 2", priority=Priority.LOW),
        ]
        mock_list_tasks.return_value = mock_tasks

        result = list_tasks_tool.invoke({})

        mock_list_tasks.assert_called_once_with(completed=None, priority=None)
        assert result == mock_tasks

    @patch("src.agent.tools.list_tasks")
    def test_list_tasks_tool_with_filters(self, mock_list_tasks: MagicMock) -> None:
        """Test listing tasks with completed and priority filters."""
        mock_tasks = [Task(id=1, title="Task 1", priority=Priority.HIGH)]
        mock_list_tasks.return_value = mock_tasks

        result = list_tasks_tool.invoke({"completed": False, "priority": "high"})

        mock_list_tasks.assert_called_once_with(completed=False, priority=Priority.HIGH)
        assert result == mock_tasks

    @patch("src.agent.tools.list_tasks")
    def test_list_tasks_tool_handles_omit_priority(self, mock_list_tasks: MagicMock) -> None:
        """Test that 'omit' priority value is treated as None."""
        mock_tasks = [Task(id=1, title="Task 1", priority=Priority.HIGH)]
        mock_list_tasks.return_value = mock_tasks

        result = list_tasks_tool.invoke({"priority": "omit"})

        mock_list_tasks.assert_called_once_with(completed=None, priority=None)
        assert result == mock_tasks
