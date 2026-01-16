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
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Literal
from sqlmodel import Session, select, or_, col
from sqlalchemy import text
from app.db import engine
from app.models import Task


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None
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

        # Validate due_date format if provided
        if due_date is not None:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                return {
                    "status": "error",
                    "message": f"due_date must be in YYYY-MM-DD format (got '{due_date}')",
                    "data": None
                }

        # Create task
        now = datetime.now(timezone.utc)
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
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
            else:
                # due_date not in current model, fallback to created_at
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
    task_id: int
) -> Dict[str, Any]:
    """
    Permanently delete a task.

    Args:
        user_id: The authenticated user's ID (required for user isolation)
        task_id: The ID of the task to delete

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

            # Apply case-insensitive search on title and description
            search_pattern = f"%{keyword.lower()}%"
            statement = statement.where(
                or_(
                    col(Task.title).ilike(search_pattern),
                    col(Task.description).ilike(search_pattern)
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
