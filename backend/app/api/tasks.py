from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.enums import TaskPriority, TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.ai import BatchTaskCreate, SubtaskSuggestionResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.ai_service import generate_subtask_suggestions

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new task within a project.
    Strictly verifies that the parent project exists and is owned by current_user.
    """
    project = db.get(Project, task_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {task_in.project_id} does not exist.",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add tasks to this project.",
        )

    task = Task(
        title=task_in.title.strip(),
        description=task_in.description.strip() if task_in.description else None,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        project_id=task_in.project_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/batch", response_model=list[TaskResponse], status_code=status.HTTP_201_CREATED)
def batch_create_tasks(
    batch_in: BatchTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Batch create tasks (e.g. approving selected AI subtask suggestions).
    Strictly verifies ownership of target project.
    """
    project = db.get(Project, batch_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {batch_in.project_id} does not exist.",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add tasks to this project.",
        )

    created_tasks: list[Task] = []
    for item in batch_in.tasks:
        task = Task(
            title=item.title.strip(),
            description=item.description.strip() if item.description else None,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            due_date=None,
            project_id=batch_in.project_id,
        )
        db.add(task)
        created_tasks.append(task)

    db.commit()
    for task in created_tasks:
        db.refresh(task)
    return created_tasks


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    project_id: int | None = Query(default=None, description="Filter tasks by project ID"),
    status: TaskStatus | None = Query(default=None, description="Filter tasks by status"),
    priority: TaskPriority | None = Query(default=None, description="Filter tasks by priority"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List tasks owned by current user via parent project, with optional filters."""
    query = (
        db.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter(Project.owner_id == current_user.id)
    )
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    if status is not None:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)

    return query.order_by(Task.id.asc()).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a task by ID, strictly enforcing project ownership."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found.",
        )
    if task.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task.",
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Partially update an existing task, strictly enforcing project ownership."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found.",
        )
    if task.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task.",
        )

    update_data = task_in.model_dump(exclude_unset=True)
    if "title" in update_data and update_data["title"] is not None:
        task.title = update_data["title"].strip()
    if "description" in update_data:
        task.description = (
            update_data["description"].strip()
            if update_data["description"] is not None
            else None
        )
    if "status" in update_data and update_data["status"] is not None:
        task.status = update_data["status"]
    if "priority" in update_data and update_data["priority"] is not None:
        task.priority = update_data["priority"]
    if "due_date" in update_data:
        task.due_date = update_data["due_date"]

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a task by ID, strictly enforcing project ownership."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found.",
        )
    if task.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task.",
        )

    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/suggest-subtasks", response_model=SubtaskSuggestionResponse)
def suggest_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI subtask suggestions for a task.
    Strictly verifies task ownership. Does NOT auto-save suggestions to DB.
    """
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found.",
        )
    if task.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to generate suggestions for this task.",
        )

    return generate_subtask_suggestions(
        task_id=task.id,
        title=task.title,
        description=task.description,
        status_str=task.status.value,
        priority_str=task.priority.value,
        due_date_str=task.due_date.isoformat() if task.due_date else None,
    )
