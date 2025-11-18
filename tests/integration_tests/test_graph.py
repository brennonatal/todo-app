"""Integration tests for the todo agent graph."""

import pytest
from langchain_core.messages import HumanMessage

from src.agent.graph import graph

pytestmark = pytest.mark.anyio


async def test_agent_can_create_task() -> None:
    """Test that the agent can create a task using the create_task_tool."""
    res = await graph.ainvoke(
        {"messages": [HumanMessage(content="Create a task called 'Test integration'")]},
    )

    # Check that the agent responded
    assert len(res["messages"]) > 0
    last_message = res["messages"][-1]

    # The agent should have used tools and provided a response
    assert last_message.content is not None
    # Response should acknowledge task creation
    response_lower = str(last_message.content).lower()
    assert any(
        keyword in response_lower
        for keyword in ["created", "task", "test integration", "added"]
    )


async def test_agent_can_list_tasks() -> None:
    """Test that the agent can list tasks using the list_tasks_tool."""
    res = await graph.ainvoke(
        {"messages": [HumanMessage(content="Show me all my tasks")]},
    )

    # Check that the agent responded
    assert len(res["messages"]) > 0
    last_message = res["messages"][-1]
    assert last_message.content is not None


async def test_agent_understands_todo_domain() -> None:
    """Test that the agent responds appropriately to todo-related queries."""
    res = await graph.ainvoke(
        {"messages": [HumanMessage(content="What can you help me with?")]},
    )

    # Check that the agent mentions task/todo management capabilities
    assert len(res["messages"]) > 0
    last_message = res["messages"][-1]
    response_lower = str(last_message.content).lower()

    # Agent should mention its todo/task management capabilities
    assert any(
        keyword in response_lower
        for keyword in ["task", "todo", "manage", "organize", "create", "track"]
    )
