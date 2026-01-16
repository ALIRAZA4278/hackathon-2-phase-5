"""
Task CRUD API endpoints.
Per specs/api/rest-endpoints.md

Security: Every endpoint:
1. Requires JWT authentication
2. Verifies URL user_id matches JWT user_id
3. Filters queries by user_id
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.dependencies import get_current_user, verify_user_access

router = APIRouter(tags=["tasks"])


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskListResponse:
    """
    List all tasks for the authenticated user.
    GET /api/{user_id}/tasks
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    # Query tasks filtered by user_id
    statement = select(Task).where(Task.user_id == current_user).order_by(Task.created_at.desc())
    tasks = db.exec(statement).all()

    return TaskListResponse(tasks=tasks, count=len(tasks))


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.
    POST /api/{user_id}/tasks
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    # Create task with user_id from JWT (not from request body)
    now = datetime.now(timezone.utc)
    task = Task(
        user_id=current_user,  # Always use JWT user_id
        title=task_data.title,
        description=task_data.description,
        completed=False,
        created_at=now,
        updated_at=now
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Get a specific task by ID.
    GET /api/{user_id}/tasks/{task_id}
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    # Query task with user_id filter (prevents enumeration)
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Update a task (title and description only).
    PUT /api/{user_id}/tasks/{task_id}
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    # Query task with user_id filter
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields
    task.title = task_data.title
    task.description = task_data.description
    task.updated_at = datetime.now(timezone.utc)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a task permanently.
    DELETE /api/{user_id}/tasks/{task_id}
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    # Query task with user_id filter
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Toggle task completion status.
    PATCH /api/{user_id}/tasks/{task_id}/complete
    """
    # Security: Verify user access
    verify_user_access(user_id, current_user)

    # Query task with user_id filter
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task
