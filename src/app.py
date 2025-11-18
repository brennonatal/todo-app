"""Streamlit TODO application with AI agent integration."""

import logging
import os
from datetime import datetime

import httpx
import streamlit as st
from langgraph_sdk import get_sync_client

from src.db.functions import (
    create_task,
    delete_task,
    edit_task,
    list_tasks,
)
from src.models import Priority, RepeatInterval

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="TODO App",
    page_icon="✓",
    layout="wide",
)

# Initialize LangGraph client
LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://localhost:8123")


@st.cache_resource
def get_langgraph_client():
    """Get LangGraph sync client with connection pooling."""
    try:
        # Test connection first
        with httpx.Client() as http_client:
            response = http_client.get(f"{LANGGRAPH_URL}/ok", timeout=2.0)
            if response.status_code == 200:
                return get_sync_client(url=LANGGRAPH_URL)
    except Exception:
        pass
    return None


client = get_langgraph_client()

st.title("✓ TODO App with AI Assistant")

# Create tabs for different modes
tab1, tab2 = st.tabs(["🤖 AI Assistant", "📝 Manual Mode"])

# ============================================================================
# TAB 1: AI Assistant
# ============================================================================
with tab1:
    st.header("AI Task Assistant")

    if client is None:
        st.error(
            f"⚠️ LangGraph server not available at {LANGGRAPH_URL}. "
            "Make sure all Docker services are running."
        )
        st.info("Run `docker-compose up` to start all services including the AI agent.")
    else:
        st.success("✅ AI Assistant connected and ready!")

        # Initialize chat history in session state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me to manage your tasks..."):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get agent response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("_Thinking..._")
                full_response = ""

                try:
                    # Build full conversation history for context
                    messages_for_agent = []
                    for msg in st.session_state.messages:
                        role = "human" if msg["role"] == "user" else "ai"
                        messages_for_agent.append({"role": role, "content": msg["content"]})
                    # Add current message
                    messages_for_agent.append({"role": "human", "content": prompt})

                    # Stream the agent's response using sync client
                    for chunk in client.runs.stream(
                        None,  # thread_id - None for threadless run
                        "agent",  # Assistant ID from langgraph.json
                        input={"messages": messages_for_agent},
                        stream_mode="values",
                    ):
                        # Process streaming chunks with values mode
                        # Only extract final response, don't show intermediate steps
                        if hasattr(chunk, "data") and chunk.data:
                            if isinstance(chunk.data, dict) and "messages" in chunk.data:
                                messages = chunk.data["messages"]
                                if messages and len(messages) > 0:
                                    # Get the last message if it's from AI
                                    last_msg = messages[-1]

                                    # Check if this is an AI message
                                    is_ai_msg = False
                                    if isinstance(last_msg, dict):
                                        is_ai_msg = last_msg.get("type") == "ai"

                                    if is_ai_msg:
                                        # Extract content
                                        content = None
                                        if hasattr(last_msg, "content"):
                                            content = last_msg.content
                                        elif isinstance(last_msg, dict) and "content" in last_msg:
                                            content = last_msg["content"]

                                        if content:
                                            full_response = str(content)

                    # Display final response only
                    if full_response:
                        message_placeholder.markdown(full_response)
                    else:
                        full_response = (
                            "I processed your request but didn't generate a response."
                        )
                        message_placeholder.markdown(full_response)

                    # Add assistant response to history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )

                except Exception as e:
                    import traceback

                    error_msg = f"Error communicating with AI: {str(e)}"
                    st.error(error_msg)
                    st.error(f"Details: {traceback.format_exc()}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

        # Sidebar with chat controls
        st.sidebar.header("Chat Controls")
        if st.sidebar.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        st.sidebar.divider()
        st.sidebar.caption("💡 **Tips:**")
        st.sidebar.caption("• 'Create a task to buy groceries'")
        st.sidebar.caption("• 'Show me my high priority tasks'")
        st.sidebar.caption("• 'Mark task #5 as complete'")
        st.sidebar.caption("• 'What tasks are due this week?'")

# ============================================================================
# TAB 2: Manual Mode
# ============================================================================
with tab2:
    # Sidebar for filters
    st.sidebar.header("Filters")
    show_completed = st.sidebar.checkbox("Show completed tasks", value=False)
    priority_filter = st.sidebar.selectbox(
        "Filter by priority",
        options=[None, Priority.HIGH, Priority.MEDIUM, Priority.LOW],
        format_func=lambda x: "All priorities" if x is None else x.value.title(),
    )

    # Main section - Create new task
    st.header("Create New Task")

    with st.form("new_task_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            new_title = st.text_input("Title", placeholder="Enter task title...")

        with col2:
            new_priority = st.selectbox(
                "Priority",
                options=[Priority.HIGH, Priority.MEDIUM, Priority.LOW],
                format_func=lambda x: x.value.title(),
            )

        new_description = st.text_area(
            "Description", placeholder="Task description (optional)"
        )

        col3, col4, col5 = st.columns(3)

        with col3:
            new_due_date = st.date_input("Due date", value=None)

        with col4:
            new_time_estimate = st.selectbox(
                "Time estimate",
                options=[None, 5, 15, 30, 60, 120, 240],
                format_func=lambda x: "No estimate" if x is None else f"{x} minutes",
            )

        with col5:
            new_repeat = st.selectbox(
                "Repeat",
                options=[
                    None,
                    RepeatInterval.HOURLY,
                    RepeatInterval.DAILY,
                    RepeatInterval.WEEKLY,
                    RepeatInterval.MONTHLY,
                ],
                format_func=lambda x: "No repeat" if x is None else x.value.title(),
            )

        submit_button = st.form_submit_button("Add Task", use_container_width=True)

        if submit_button and new_title:
            try:
                create_task(
                    title=new_title,
                    description=new_description if new_description else None,
                    priority=new_priority,
                    due_date=datetime.combine(new_due_date, datetime.min.time())
                    if new_due_date
                    else None,
                    time_estimate_minutes=new_time_estimate,
                    repeat_interval=new_repeat,
                )
                st.success(f"Task '{new_title}' created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating task: {e}")

    # Task list section
    st.header("Tasks")

    # Fetch tasks with filters
    tasks = list_tasks(
        completed=show_completed if show_completed else False,
        priority=priority_filter,
    )

    if not tasks:
        st.info("No tasks found. Create one above!")
    else:
        for task in tasks:
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 4, 2, 1])

                with col1:
                    # Checkbox to mark complete
                    is_completed = st.checkbox(
                        "Done",
                        value=task.completed,
                        key=f"complete_{task.id}",
                        label_visibility="collapsed",
                    )
                    if is_completed != task.completed and task.id is not None:
                        edit_task(task.id, completed=is_completed)
                        st.rerun()

                with col2:
                    # Task title and description
                    st.markdown(f"**{task.title}**")
                    if task.description:
                        st.caption(task.description)

                with col3:
                    # Priority badge
                    priority_colors = {
                        Priority.HIGH: "🔴",
                        Priority.MEDIUM: "🟡",
                        Priority.LOW: "🟢",
                    }
                    st.text(
                        f"{priority_colors[task.priority]} {task.priority.value.title()}"
                    )

                    # Due date if set
                    if task.due_date:
                        st.caption(f"Due: {task.due_date.strftime('%Y-%m-%d')}")

                with col4:
                    # Delete button
                    if (
                        st.button("Delete", key=f"delete_{task.id}")
                        and task.id is not None
                    ):
                        delete_task(task.id)
                        st.success("Task deleted!")
                        st.rerun()

                st.divider()

    # Footer
    st.sidebar.divider()
    st.sidebar.caption(f"Total tasks: {len(tasks)}")
