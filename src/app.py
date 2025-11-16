"""Streamlit TODO application."""
import streamlit as st
from datetime import datetime

from src.db.functions import list_tasks, create_task, edit_task, delete_task
from src.db.functions import list_tags, add_tag_to_task, remove_tag_from_task
from src.models import Priority, RepeatInterval

# Page config
st.set_page_config(
    page_title="TODO App",
    page_icon="✓",
    layout="wide",
)

st.title("✓ TODO App")

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

    new_description = st.text_area("Description", placeholder="Task description (optional)")

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
            options=[None, RepeatInterval.HOURLY, RepeatInterval.DAILY,
                    RepeatInterval.WEEKLY, RepeatInterval.MONTHLY],
            format_func=lambda x: "No repeat" if x is None else x.value.title(),
        )

    submit_button = st.form_submit_button("Add Task", use_container_width=True)

    if submit_button and new_title:
        try:
            create_task(
                title=new_title,
                description=new_description if new_description else None,
                priority=new_priority,
                due_date=datetime.combine(new_due_date, datetime.min.time()) if new_due_date else None,
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
                if is_completed != task.completed:
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
                st.text(f"{priority_colors[task.priority]} {task.priority.value.title()}")

                # Due date if set
                if task.due_date:
                    st.caption(f"Due: {task.due_date.strftime('%Y-%m-%d')}")

            with col4:
                # Delete button
                if st.button("Delete", key=f"delete_{task.id}"):
                    delete_task(task.id)
                    st.success(f"Task deleted!")
                    st.rerun()

            st.divider()

# Footer
st.sidebar.divider()
st.sidebar.caption(f"Total tasks: {len(tasks)}")
