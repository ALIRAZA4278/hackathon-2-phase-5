"""
MCP (Model Context Protocol) tools for Todo AI Chatbot.

These tools provide AI agents with reliable, type-safe interfaces
to task management operations.

Security:
- All tools require user_id for user isolation
- Database queries filtered by user_id
- Input validation on all parameters
- Consistent error handling

Response Format:
All tools return:
{
    "status": "success" | "error",
    "message": "Human-readable description",
    "data": <relevant data or null>
}
"""
import json as json_module
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Literal
from sqlmodel import Session, select, or_, col
from sqlalchemy import text, cast, String
from app.db import engine
from app.models import Task, Reminder


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    reminder_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new todo task for the specified user.

    Args:
        user_id: The authenticated user's ID (required for user isolation)
        title: Task title (1-200 characters, required)
        description: Optional task description (max 1000 characters)
        due_date: Optional due date in YYYY-MM-DD format

    Returns:
        ToolResponse with status, message, and task data:
        {
            "status": "success",
            "message": "Task created successfully",
            "data": {
                "id": 47,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": false,
                "created_at": "2025-01-16T19:30:00Z",
                "updated_at": "2025-01-16T19:30:00Z"
            }
        }

    Note:
        - completed is always set to false for new tasks
        - created_at and updated_at are automatically set to current UTC time
        - due_date is currently stored but not enforced in the model
    """
    try:
        # Input validation
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        if not title or not title.strip():
            return {
                "status": "error",
                "message": "title is required and cannot be empty",
                "data": None
            }

        # Validate title length
        title = title.strip()
        if len(title) > 200:
            return {
                "status": "error",
                "message": f"title exceeds maximum length of 200 characters (got {len(title)})",
                "data": None
            }

        # Validate description length if provided
        if description is not None:
            description = description.strip() if description.strip() else None
            if description and len(description) > 1000:
                return {
                    "status": "error",
                    "message": f"description exceeds maximum length of 1000 characters (got {len(description)})",
                    "data": None
                }

        # Validate priority if provided
        valid_priorities = ["low", "medium", "high", "urgent"]
        task_priority = "medium"
        if priority is not None:
            if priority not in valid_priorities:
                return {
                    "status": "error",
                    "message": f"priority must be one of {valid_priorities} (got '{priority}')",
                    "data": None
                }
            task_priority = priority

        # Validate reminder_time format if provided
        parsed_reminder_time = None
        if reminder_time is not None:
            try:
                parsed_reminder_time = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))
            except ValueError:
                return {
                    "status": "error",
                    "message": f"reminder_time must be in ISO 8601 format (got '{reminder_time}')",
                    "data": None
                }

        # Parse due_date to datetime if provided
        parsed_due_date = None
        if due_date is not None:
            try:
                parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return {
                    "status": "error",
                    "message": f"due_date must be in YYYY-MM-DD format (got '{due_date}')",
                    "data": None
                }

        # Normalize tags
        task_tags = tags if tags else []

        # Create task
        now = datetime.now(timezone.utc)
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            priority=task_priority,
            tags=task_tags,
            due_date=parsed_due_date,
            reminder_time=parsed_reminder_time,
            created_at=now,
            updated_at=now
        )

        # Save to database
        with Session(engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "message": "Task created successfully",
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "tags": task.tags or [],
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                    "recurring_rule": task.recurring_rule,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}",
            "data": None
        }


async def list_tasks(
    user_id: str,
    status: Literal["all", "pending", "completed"] = "all",
    limit: int = 50,
    offset: int = 0,
    sort_by: Optional[Literal["created_at", "title", "due_date"]] = None,
    sort_order: Literal["asc", "desc"] = "desc"
) -> Dict[str, Any]:
    """
    List tasks for the specified user with optional filtering and sorting.

    Args:
        user_id: The authenticated user's ID (required for user isolation)
        status: Filter by completion status - "all", "pending", or "completed" (default: "all")
        limit: Maximum number of tasks to return (default: 50)
        offset: Number of tasks to skip for pagination (default: 0)
        sort_by: Field to sort by - "created_at", "title", or "due_date" (default: "created_at")
        sort_order: Sort order - "asc" or "desc" (default: "desc")

    Returns:
        ToolResponse with status, message, and task list:
        {
            "status": "success",
            "message": "Found 8 pending tasks",
            "data": {
                "tasks": [
                    {
                        "id": 47,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": false,
                        "created_at": "2025-01-16T19:30:00Z",
                        "updated_at": "2025-01-16T19:30:00Z"
                    },
                    ...
                ],
                "total": 12,
                "returned": 8
            }
        }
    """
    try:
        # Input validation
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        if status not in ["all", "pending", "completed"]:
            return {
                "status": "error",
                "message": f"status must be 'all', 'pending', or 'completed' (got '{status}')",
                "data": None
            }

        if limit < 1:
            return {
                "status": "error",
                "message": f"limit must be at least 1 (got {limit})",
                "data": None
            }

        if offset < 0:
            return {
                "status": "error",
                "message": f"offset must be non-negative (got {offset})",
                "data": None
            }

        if sort_by is not None and sort_by not in ["created_at", "title", "due_date"]:
            return {
                "status": "error",
                "message": f"sort_by must be 'created_at', 'title', or 'due_date' (got '{sort_by}')",
                "data": None
            }

        if sort_order not in ["asc", "desc"]:
            return {
                "status": "error",
                "message": f"sort_order must be 'asc' or 'desc' (got '{sort_order}')",
                "data": None
            }

        with Session(engine) as session:
            # Build base query filtered by user_id
            statement = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)

            # Get total count before pagination
            count_statement = statement
            total_count = len(session.exec(count_statement).all())

            # Apply sorting
            sort_field = sort_by if sort_by else "created_at"
            if sort_field == "created_at":
                order_col = Task.created_at
            elif sort_field == "title":
                order_col = Task.title
            elif sort_field == "due_date":
                order_col = Task.due_date
            else:
                order_col = Task.created_at

            if sort_order == "asc":
                statement = statement.order_by(order_col.asc())
            else:
                statement = statement.order_by(order_col.desc())

            # Apply pagination
            statement = statement.offset(offset).limit(limit)

            # Execute query
            tasks = session.exec(statement).all()

            # Build response message
            status_text = status if status != "all" else ""
            if status_text:
                message = f"Found {len(tasks)} {status_text} tasks"
            else:
                message = f"Found {len(tasks)} tasks"

            return {
                "status": "success",
                "message": message,
                "data": {
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "completed": task.completed,
                            "priority": task.priority,
                            "tags": task.tags or [],
                            "due_date": task.due_date.isoformat() if task.due_date else None,
                            "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                            "recurring_rule": task.recurring_rule,
                            "created_at": task.created_at.isoformat(),
                            "updated_at": task.updated_at.isoformat()
                        }
                        for task in tasks
                    ],
                    "total": total_count,
                    "returned": len(tasks)
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list tasks: {str(e)}",
            "data": None
        }


async def toggle_task_completion(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Toggle the completion status of a task.

    Args:
        user_id: The authenticated user's ID (required for user isolation)
        task_id: The ID of the task to toggle

    Returns:
        ToolResponse with status, message, and updated task data:
        {
            "status": "success",
            "message": "Task marked as completed",
            "data": {
                "task_id": 47,
                "title": "Buy groceries",
                "completed": true,
                "updated_at": "2025-01-16T19:45:00Z"
            }
        }

    Note:
        - Returns error if task not found or doesn't belong to user
        - Automatically updates updated_at timestamp
    """
    try:
        # Input validation
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        if task_id < 1:
            return {
                "status": "error",
                "message": f"task_id must be a positive integer (got {task_id})",
                "data": None
            }

        with Session(engine) as session:
            # Query task with user_id filter (prevents unauthorized access)
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {
                    "status": "error",
                    "message": f"Task not found with id {task_id}",
                    "data": None
                }

            # Toggle completion status
            task.completed = not task.completed
            task.updated_at = datetime.now(timezone.utc)

            session.add(task)
            session.commit()
            session.refresh(task)

            # Build message based on new status
            status_text = "completed" if task.completed else "pending"
            message = f"Task marked as {status_text}"

            return {
                "status": "success",
                "message": message,
                "data": {
                    "task_id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "priority": task.priority,
                    "tags": task.tags or [],
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                    "recurring_rule": task.recurring_rule,
                    "updated_at": task.updated_at.isoformat()
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to toggle task completion: {str(e)}",
            "data": None
        }


async def delete_task(
    user_id: str,
    task_id: int,
    confirmed: bool = False
) -> Dict[str, Any]:
    """
    Permanently delete a task (requires confirmation).

    Args:
        user_id: The authenticated user's ID (required for user isolation)
        task_id: The ID of the task to delete
        confirmed: Must be True to actually delete. If False, returns confirmation prompt.

    Returns:
        ToolResponse with status, message, and deleted task info:
        {
            "status": "success",
            "message": "Task 'Buy groceries' has been deleted",
            "data": {
                "deleted_task_id": 47,
                "deleted_title": "Buy groceries"
            }
        }

    Note:
        - Returns error if task not found or doesn't belong to user
        - Deletion is permanent and cannot be undone
        - If confirmed=False, returns a confirmation request instead of deleting
    """
    try:
        # Input validation
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        if task_id < 1:
            return {
                "status": "error",
                "message": f"task_id must be a positive integer (got {task_id})",
                "data": None
            }

        with Session(engine) as session:
            # Query task with user_id filter (prevents unauthorized access)
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {
                    "status": "error",
                    "message": f"Task not found with id {task_id}",
                    "data": None
                }

            # If not confirmed, return confirmation request
            if not confirmed:
                return {
                    "status": "confirmation_required",
                    "message": f"Are you sure you want to delete task '{task.title}' (ID: {task.id})? This action cannot be undone. Call delete_task again with confirmed=true to proceed.",
                    "data": {
                        "task_id": task.id,
                        "title": task.title,
                        "priority": task.priority,
                        "tags": task.tags or [],
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                        "recurring_rule": task.recurring_rule,
                        "requires_confirmation": True
                    }
                }

            # Store task info before deletion
            deleted_id = task.id
            deleted_title = task.title

            # Delete task
            session.delete(task)
            session.commit()

            return {
                "status": "success",
                "message": f"Task '{deleted_title}' has been deleted",
                "data": {
                    "deleted_task_id": deleted_id,
                    "deleted_title": deleted_title
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}",
            "data": None
        }


async def get_my_user_info(
    user_id: str
) -> Dict[str, Any]:
    """
    Get basic information about the currently logged-in user.

    Args:
        user_id: The authenticated user's ID (required for user isolation)

    Returns:
        ToolResponse with status, message, and user info:
        {
            "status": "success",
            "message": "Here is your account information",
            "data": {
                "email": "ali@example.com",
                "name": "ALI",
                "created_at": "2024-11-05T14:20:00Z"
            }
        }

    Note:
        - Only returns safe, non-sensitive information
        - Useful for queries like "who am i", "my email kya hai", "meri account info dikhao"
        - NEVER returns password, tokens, or sensitive fields
    """
    try:
        # Input validation
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        with Session(engine) as session:
            # Query the Better Auth user table directly
            # Better Auth creates a "user" table with standard fields
            result = session.execute(
                text("""
                    SELECT id, email, name, "createdAt", "updatedAt"
                    FROM "user"
                    WHERE id = :user_id
                """),
                {"user_id": user_id}
            )
            row = result.fetchone()

            if not row:
                return {
                    "status": "error",
                    "message": "User not found",
                    "data": None
                }

            # Build response with safe fields only
            user_data = {
                "id": row[0],
                "email": row[1],
                "name": row[2] if row[2] else None,
                "created_at": row[3].isoformat() if row[3] else None,
            }

            return {
                "status": "success",
                "message": "Here is your account information",
                "data": user_data
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get user info: {str(e)}",
            "data": None
        }


async def search_tasks(
    user_id: str,
    keyword: str,
    status: Optional[Literal["all", "pending", "completed"]] = "all"
) -> Dict[str, Any]:
    """
    Search through user's tasks by keyword in title or description.

    Args:
        user_id: The authenticated user's ID (required for user isolation)
        keyword: Search term (required)
        status: Filter by completion status - "all", "pending", or "completed" (default: "all")

    Returns:
        ToolResponse with status, message, and matching tasks:
        {
            "status": "success",
            "message": "Found 3 tasks matching 'groceries'",
            "data": {
                "tasks": [
                    {
                        "id": 42,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": false,
                        "created_at": "2025-01-16T19:30:00Z"
                    }
                ],
                "search_term": "groceries",
                "total": 3
            }
        }

    Note:
        - Case-insensitive search in both title AND description
        - Only returns current user's tasks (user isolation enforced)
        - Results ordered by creation date (newest first)
    """
    try:
        # Input validation
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        if not keyword or not keyword.strip():
            return {
                "status": "error",
                "message": "keyword is required and cannot be empty",
                "data": None
            }

        keyword = keyword.strip()

        if status not in ["all", "pending", "completed"]:
            return {
                "status": "error",
                "message": f"status must be 'all', 'pending', or 'completed' (got '{status}')",
                "data": None
            }

        with Session(engine) as session:
            # Build base query with user isolation
            statement = select(Task).where(Task.user_id == user_id)

            # Apply case-insensitive search on title, description, and tags
            search_pattern = f"%{keyword.lower()}%"
            statement = statement.where(
                or_(
                    col(Task.title).ilike(search_pattern),
                    col(Task.description).ilike(search_pattern),
                    cast(Task.tags, String).ilike(search_pattern)
                )
            )

            # Apply status filter
            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)

            # Order by creation date (newest first)
            statement = statement.order_by(Task.created_at.desc())

            # Execute query
            tasks = session.exec(statement).all()

            # Build response message
            status_suffix = f" {status}" if status != "all" else ""
            if len(tasks) == 0:
                message = f"No{status_suffix} tasks found matching '{keyword}'"
            elif len(tasks) == 1:
                message = f"Found 1{status_suffix} task matching '{keyword}'"
            else:
                message = f"Found {len(tasks)}{status_suffix} tasks matching '{keyword}'"

            return {
                "status": "success",
                "message": message,
                "data": {
                    "tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "description": task.description,
                            "completed": task.completed,
                            "priority": task.priority,
                            "tags": task.tags or [],
                            "due_date": task.due_date.isoformat() if task.due_date else None,
                            "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                            "recurring_rule": task.recurring_rule,
                            "created_at": task.created_at.isoformat(),
                            "updated_at": task.updated_at.isoformat()
                        }
                        for task in tasks
                    ],
                    "search_term": keyword,
                    "total": len(tasks)
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to search tasks: {str(e)}",
            "data": None
        }


# ============================================================================
# Phase V: Advanced Task Management Tools (T035-T041)
# ============================================================================


def _build_task_data(task: Task) -> Dict[str, Any]:
    """Helper to build standardized task data dict with all fields."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "tags": task.tags or [],
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
        "recurring_rule": task.recurring_rule,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


def _validate_task_ownership(session: Session, user_id: str, task_id: int):
    """
    Validate that a task exists and belongs to the given user.

    Returns:
        (task, None) on success, (None, error_response) on failure.
    """
    if not user_id or not user_id.strip():
        return None, {
            "status": "error",
            "message": "user_id is required and cannot be empty",
            "data": None
        }

    if task_id < 1:
        return None, {
            "status": "error",
            "message": f"task_id must be a positive integer (got {task_id})",
            "data": None
        }

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        return None, {
            "status": "error",
            "message": f"Task not found with id {task_id}",
            "data": None
        }

    return task, None


async def set_due_date(
    user_id: str,
    task_id: int,
    due_date: str
) -> Dict[str, Any]:
    """
    Set or update the due date for a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task
        due_date: Due date in YYYY-MM-DD format

    Returns:
        ToolResponse with updated task data
    """
    try:
        # Validate due_date format
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return {
                "status": "error",
                "message": f"due_date must be in YYYY-MM-DD format (got '{due_date}')",
                "data": None
            }

        with Session(engine) as session:
            task, error = _validate_task_ownership(session, user_id, task_id)
            if error:
                return error

            task.due_date = parsed_date
            task.updated_at = datetime.now(timezone.utc)

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "message": f"Due date for '{task.title}' set to {due_date}",
                "data": _build_task_data(task)
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to set due date: {str(e)}",
            "data": None
        }


async def schedule_reminder(
    user_id: str,
    task_id: int,
    trigger_at: str
) -> Dict[str, Any]:
    """
    Schedule a reminder for a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task
        trigger_at: When to trigger the reminder (ISO 8601 datetime string)

    Returns:
        ToolResponse with reminder data
    """
    try:
        # Validate trigger_at format
        try:
            parsed_trigger = datetime.fromisoformat(trigger_at.replace("Z", "+00:00"))
        except ValueError:
            return {
                "status": "error",
                "message": f"trigger_at must be in ISO 8601 format (got '{trigger_at}')",
                "data": None
            }

        with Session(engine) as session:
            task, error = _validate_task_ownership(session, user_id, task_id)
            if error:
                return error

            # Create Reminder record
            reminder = Reminder(
                task_id=task_id,
                user_id=user_id,
                trigger_at=parsed_trigger,
                status="pending",
                created_at=datetime.now(timezone.utc)
            )

            session.add(reminder)
            session.commit()
            session.refresh(reminder)

            return {
                "status": "success",
                "message": f"Reminder scheduled for '{task.title}' at {trigger_at}",
                "data": {
                    "reminder_id": reminder.id,
                    "task_id": reminder.task_id,
                    "task_title": task.title,
                    "trigger_at": reminder.trigger_at.isoformat(),
                    "status": reminder.status,
                    "created_at": reminder.created_at.isoformat()
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to schedule reminder: {str(e)}",
            "data": None
        }


async def create_recurring(
    user_id: str,
    task_id: int,
    frequency: str,
    interval: int = 1,
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None,
    cron_expression: Optional[str] = None
) -> Dict[str, Any]:
    """
    Set a recurring rule for a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task
        frequency: Recurrence frequency - daily, weekly, monthly, yearly, custom
        interval: How often (e.g., every 2 weeks). Default: 1
        day_of_week: Day of week (0=Monday, 6=Sunday) for weekly recurrence
        day_of_month: Day of month (1-31) for monthly recurrence
        cron_expression: Custom cron expression (for frequency=custom)

    Returns:
        ToolResponse with updated task data including recurring_rule
    """
    try:
        valid_frequencies = ["daily", "weekly", "monthly", "yearly", "custom"]
        if frequency not in valid_frequencies:
            return {
                "status": "error",
                "message": f"frequency must be one of {valid_frequencies} (got '{frequency}')",
                "data": None
            }

        if interval < 1:
            return {
                "status": "error",
                "message": f"interval must be at least 1 (got {interval})",
                "data": None
            }

        if day_of_week is not None and (day_of_week < 0 or day_of_week > 6):
            return {
                "status": "error",
                "message": f"day_of_week must be 0-6 (got {day_of_week})",
                "data": None
            }

        if day_of_month is not None and (day_of_month < 1 or day_of_month > 31):
            return {
                "status": "error",
                "message": f"day_of_month must be 1-31 (got {day_of_month})",
                "data": None
            }

        with Session(engine) as session:
            task, error = _validate_task_ownership(session, user_id, task_id)
            if error:
                return error

            # Build recurring rule JSON
            recurring_rule = {
                "frequency": frequency,
                "interval": interval,
            }
            if day_of_week is not None:
                recurring_rule["day_of_week"] = day_of_week
            if day_of_month is not None:
                recurring_rule["day_of_month"] = day_of_month
            if cron_expression is not None:
                recurring_rule["cron_expression"] = cron_expression

            task.recurring_rule = recurring_rule
            task.updated_at = datetime.now(timezone.utc)

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "message": f"Recurring rule set for '{task.title}': {frequency} (every {interval})",
                "data": _build_task_data(task)
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create recurring rule: {str(e)}",
            "data": None
        }


async def set_priority(
    user_id: str,
    task_id: int,
    priority: str
) -> Dict[str, Any]:
    """
    Set the priority level for a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task
        priority: Priority level - low, medium, high, urgent

    Returns:
        ToolResponse with updated task data
    """
    try:
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority not in valid_priorities:
            return {
                "status": "error",
                "message": f"priority must be one of {valid_priorities} (got '{priority}')",
                "data": None
            }

        with Session(engine) as session:
            task, error = _validate_task_ownership(session, user_id, task_id)
            if error:
                return error

            task.priority = priority
            task.updated_at = datetime.now(timezone.utc)

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "message": f"Priority for '{task.title}' set to {priority}",
                "data": _build_task_data(task)
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to set priority: {str(e)}",
            "data": None
        }


async def add_tags(
    user_id: str,
    task_id: int,
    tags: List[str]
) -> Dict[str, Any]:
    """
    Add tags to a task (deduplicates).

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task
        tags: List of tag strings to add

    Returns:
        ToolResponse with updated task data
    """
    try:
        if not tags or len(tags) == 0:
            return {
                "status": "error",
                "message": "tags must be a non-empty list of strings",
                "data": None
            }

        # Clean tags
        clean_tags = [t.strip().lower() for t in tags if t and t.strip()]
        if not clean_tags:
            return {
                "status": "error",
                "message": "tags must contain at least one non-empty string",
                "data": None
            }

        with Session(engine) as session:
            task, error = _validate_task_ownership(session, user_id, task_id)
            if error:
                return error

            # Merge with existing tags, deduplicate
            existing_tags = task.tags or []
            merged = list(set(existing_tags + clean_tags))
            task.tags = merged
            task.updated_at = datetime.now(timezone.utc)

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "success",
                "message": f"Tags updated for '{task.title}': {', '.join(merged)}",
                "data": _build_task_data(task)
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to add tags: {str(e)}",
            "data": None
        }


async def filter_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filter tasks by multiple criteria.

    Args:
        user_id: The authenticated user's ID
        status: Filter by status - pending, completed (None for all)
        priority: Filter by priority - low, medium, high, urgent
        tags: Filter by tags (tasks that have any of the given tags)
        due_date_from: Start of due date range (YYYY-MM-DD)
        due_date_to: End of due date range (YYYY-MM-DD)

    Returns:
        ToolResponse with filtered task list
    """
    try:
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        # Validate status
        if status is not None and status not in ["pending", "completed"]:
            return {
                "status": "error",
                "message": f"status must be 'pending' or 'completed' (got '{status}')",
                "data": None
            }

        # Validate priority
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority is not None and priority not in valid_priorities:
            return {
                "status": "error",
                "message": f"priority must be one of {valid_priorities} (got '{priority}')",
                "data": None
            }

        # Parse date filters
        parsed_from = None
        if due_date_from is not None:
            try:
                parsed_from = datetime.strptime(due_date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return {
                    "status": "error",
                    "message": f"due_date_from must be in YYYY-MM-DD format (got '{due_date_from}')",
                    "data": None
                }

        parsed_to = None
        if due_date_to is not None:
            try:
                parsed_to = datetime.strptime(due_date_to, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return {
                    "status": "error",
                    "message": f"due_date_to must be in YYYY-MM-DD format (got '{due_date_to}')",
                    "data": None
                }

        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)

            # Apply priority filter
            if priority is not None:
                statement = statement.where(Task.priority == priority)

            # Apply tags filter (match any tag)
            if tags is not None and len(tags) > 0:
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(
                        cast(Task.tags, String).ilike(f"%{tag.strip().lower()}%")
                    )
                statement = statement.where(or_(*tag_conditions))

            # Apply due date range
            if parsed_from is not None:
                statement = statement.where(Task.due_date >= parsed_from)
            if parsed_to is not None:
                statement = statement.where(Task.due_date <= parsed_to)

            # Order by created_at desc
            statement = statement.order_by(Task.created_at.desc())

            tasks = session.exec(statement).all()

            # Build filter description for message
            filters_applied = []
            if status:
                filters_applied.append(f"status={status}")
            if priority:
                filters_applied.append(f"priority={priority}")
            if tags:
                filters_applied.append(f"tags={','.join(tags)}")
            if due_date_from:
                filters_applied.append(f"from={due_date_from}")
            if due_date_to:
                filters_applied.append(f"to={due_date_to}")

            filter_desc = ", ".join(filters_applied) if filters_applied else "none"

            return {
                "status": "success",
                "message": f"Found {len(tasks)} tasks (filters: {filter_desc})",
                "data": {
                    "tasks": [_build_task_data(task) for task in tasks],
                    "total": len(tasks),
                    "filters_applied": filters_applied
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to filter tasks: {str(e)}",
            "data": None
        }


async def sort_tasks(
    user_id: str,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Sort and return all user tasks by a specified field.

    Args:
        user_id: The authenticated user's ID
        sort_by: Field to sort by - created_at, due_date, priority, title
        sort_order: Sort direction - asc, desc

    Returns:
        ToolResponse with sorted task list
    """
    try:
        if not user_id or not user_id.strip():
            return {
                "status": "error",
                "message": "user_id is required and cannot be empty",
                "data": None
            }

        valid_sort_fields = ["created_at", "due_date", "priority", "title"]
        if sort_by not in valid_sort_fields:
            return {
                "status": "error",
                "message": f"sort_by must be one of {valid_sort_fields} (got '{sort_by}')",
                "data": None
            }

        if sort_order not in ["asc", "desc"]:
            return {
                "status": "error",
                "message": f"sort_order must be 'asc' or 'desc' (got '{sort_order}')",
                "data": None
            }

        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            # For priority sorting, use a CASE expression to map to numeric values
            if sort_by == "priority":
                from sqlalchemy import case
                priority_order = case(
                    (Task.priority == "low", 1),
                    (Task.priority == "medium", 2),
                    (Task.priority == "high", 3),
                    (Task.priority == "urgent", 4),
                    else_=0
                )
                if sort_order == "asc":
                    statement = statement.order_by(priority_order.asc())
                else:
                    statement = statement.order_by(priority_order.desc())
            elif sort_by == "due_date":
                if sort_order == "asc":
                    statement = statement.order_by(Task.due_date.asc())
                else:
                    statement = statement.order_by(Task.due_date.desc())
            elif sort_by == "title":
                if sort_order == "asc":
                    statement = statement.order_by(Task.title.asc())
                else:
                    statement = statement.order_by(Task.title.desc())
            else:
                # created_at (default)
                if sort_order == "asc":
                    statement = statement.order_by(Task.created_at.asc())
                else:
                    statement = statement.order_by(Task.created_at.desc())

            tasks = session.exec(statement).all()

            return {
                "status": "success",
                "message": f"Found {len(tasks)} tasks sorted by {sort_by} ({sort_order})",
                "data": {
                    "tasks": [_build_task_data(task) for task in tasks],
                    "total": len(tasks),
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to sort tasks: {str(e)}",
            "data": None
        }
