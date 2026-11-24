from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import TaskPriority, TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new task within a project.
    Validates that the parent project exists.
    """
    project = db.get(Project, task_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {task_in.project_id} does not exist.",
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


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    project_id: int | None = Query(default=None, description="Filter tasks by project ID"),
    status: TaskStatus | None = Query(default=None, description="Filter tasks by status"),
    priority: TaskPriority | None = Query(default=None, description="Filter tasks by priority"),
    db: Session = Depends(get_db),
):
    """List tasks, optionally filtered by project_id, status, or priority."""
    query = db.query(Task)
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
    db: Session = Depends(get_db),
):
    """Get a task by ID."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found.",
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an existing task."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found.",
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
    db: Session = Depends(get_db),
):
    """Delete a task by ID."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found.",
        )

    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
