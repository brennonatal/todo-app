# LLM Tool Wrappers for Todo App - Design Document

**Date:** 2025-11-18
**Status:** Approved
**Author:** Design brainstorming session

## Overview

This document describes the design for creating LangChain tool wrappers around the existing database CRUD functions, enabling an LLM agent to interact with the todo application.

## Problem Statement

The todo app has 8 database functions (`create_task`, `list_tasks`, `edit_task`, `delete_task`, `create_tag`, `list_tags`, `add_tag_to_task`, `remove_tag_from_task`) that need to be callable by an LLM agent.

**Challenge:** LLMs generate strings and primitives, but our database functions expect:
- Enum types (`Priority`, `RepeatInterval`)
- `datetime` objects
- Integer IDs
- Type-specific optional fields

## Design Decision: Approach 2 - Shared Helper Functions

After evaluating three approaches (inline conversion, shared helpers, decorator-based), we chose **shared helper functions** for these reasons:

- **DRY principle:** Conversion logic defined once, reused across all 8 tools
- **Maintainability:** Updates to conversion logic automatically benefit all tools
- **Testability:** Helpers can be unit tested independently
- **Clarity:** Conversion logic is explicit, not "magic"
- **Right-sized:** Not over-engineered for just 8 tools

## Architecture

### File Structure

All code resides in `src/agent/tools.py`:

```
src/agent/tools.py
├── Helper Functions (top)
│   ├── parse_priority()
│   ├── parse_repeat_interval()
│   └── parse_datetime()
├── Tool Wrappers (middle)
│   ├── create_task_tool()
│   ├── list_tasks_tool()
│   ├── edit_task_tool()
│   ├── delete_task_tool()
│   ├── create_tag_tool()
│   ├── list_tags_tool()
│   ├── add_tag_to_task_tool()
│   └── remove_tag_from_task_tool()
└── TOOLS List Export (bottom)
```

### Component Design

#### Helper Functions

**1. `parse_priority(value: str) -> Priority`**
- Converts string → `Priority` enum
- Case-insensitive
- Raises `ValueError` with valid options if invalid

**2. `parse_repeat_interval(value: str) -> RepeatInterval`**
- Converts string → `RepeatInterval` enum
- Case-insensitive
- Raises `ValueError` with valid options if invalid

**3. `parse_datetime(value: str | None) -> datetime | None`**
- Converts ISO string → `datetime` object
- Returns `None` if input is `None` (for optional fields)
- Raises `ValueError` with format example if parsing fails
- Accepts formats: "YYYY-MM-DD", "YYYY-MM-DDTHH:MM:SS"

#### Tool Wrapper Pattern

Each tool wrapper follows this pattern:

1. **Decorator:** Use `@tool` from `langchain.tools`
2. **Parameters:** Accept strings/primitives (what LLM generates)
3. **Docstring:** Detailed explanation of purpose and parameters (becomes tool description for LLM)
4. **Type Conversion:** Call helper functions to convert types
5. **Database Call:** Invoke underlying database function
6. **Error Propagation:** Let exceptions flow to LLM as error messages

**Example:**
```python
@tool
def create_task_tool(
    title: str,
    description: str | None = None,
    priority: str = "medium",
    due_date: str | None = None,
    start_date: str | None = None,
    time_estimate_minutes: int | None = None,
    repeat_interval: str | None = None,
) -> Task:
    """Create a new task in the todo list.

    Args:
        title: Task title (required)
        description: Optional task description
        priority: Priority level - must be 'low', 'medium', or 'high'
        due_date: Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        start_date: Start date in ISO format
        time_estimate_minutes: Estimated completion time in minutes
        repeat_interval: How often task repeats - 'hourly', 'daily', 'weekly', or 'monthly'

    Returns:
        Created Task object with assigned ID
    """
    return create_task(
        title=title,
        description=description,
        priority=parse_priority(priority),
        due_date=parse_datetime(due_date),
        start_date=parse_datetime(start_date),
        time_estimate_minutes=time_estimate_minutes,
        repeat_interval=parse_repeat_interval(repeat_interval) if repeat_interval else None,
    )
```

#### TOOLS List

Export all tools as a list for `graph.py`:

```python
TOOLS = [
    create_task_tool,
    list_tasks_tool,
    edit_task_tool,
    delete_task_tool,
    create_tag_tool,
    list_tags_tool,
    add_tag_to_task_tool,
    remove_tag_from_task_tool,
]
```

Import in `graph.py`: `from agent.tools import TOOLS`

## Error Handling Strategy

**Principle:** Let exceptions propagate naturally to the LLM.

**Error Types:**
- **Invalid enum values:** `ValueError` with valid options listed
- **Invalid datetime format:** `ValueError` with format example
- **Task/tag not found:** `ValueError` from database function
- **Database errors:** SQLAlchemy exceptions

**Rationale:** The LLM receives error messages as `ToolMessage` responses and can adapt (retry with correct format, inform user of non-existent resource, etc.).

## Return Types

Tools return the same objects as database functions:
- `Task` objects (all attributes populated)
- `Tag` objects
- `list[Task]` for list operations
- `bool` for delete operations

LangChain automatically serializes these to JSON for LLM consumption.

## Data Flow

```
LLM generates tool call
  ↓ (string parameters)
Tool wrapper receives call
  ↓
Helper functions convert types
  ↓ (enums, datetimes)
Database function executes
  ↓
Result returned (Task/Tag/list/bool)
  ↓ (JSON serialization)
LLM receives result
```

## Tool Catalog

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `create_task_tool` | Create new task | title, priority, due_date, description, start_date, time_estimate, repeat_interval |
| `list_tasks_tool` | List tasks with filters | completed, priority |
| `edit_task_tool` | Update existing task | task_id + any fields to update |
| `delete_task_tool` | Delete task | task_id |
| `create_tag_tool` | Create new tag | name, color |
| `list_tags_tool` | List all tags | (no parameters) |
| `add_tag_to_task_tool` | Add tag to task | task_id, tag_id |
| `remove_tag_from_task_tool` | Remove tag from task | task_id, tag_id |

## Integration Points

### With LangGraph Agent

- `graph.py:36` - `model.bind_tools(TOOLS)`
- `graph.py:72` - `ToolNode(TOOLS)`

### With Database Layer

All tools import and call functions from `src.db.functions`:
- `from src.db.functions import create_task, list_tasks, edit_task, ...`

### With Data Models

Tools import enums and models for type hints:
- `from src.models import Priority, RepeatInterval, Task, Tag`

## Success Criteria

- ✅ All 8 database functions wrapped as LLM-callable tools
- ✅ Type conversions work correctly (enums, datetimes)
- ✅ Clear, informative error messages when conversions fail
- ✅ LLM can create, list, edit, delete tasks
- ✅ LLM can create, list tags and manage task-tag relationships
- ✅ Code follows DRY, clean code principles
- ✅ Integration with existing LangGraph agent skeleton

## Implementation Notes

- Use `datetime.fromisoformat()` for parsing ISO datetime strings
- Enum conversion: `Priority(value.lower())` with try/except
- All tools use type hints (required by LangChain)
- Docstrings serve dual purpose: code documentation + LLM tool descriptions
