from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_or_create_default_user
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new project.
    If owner_id is not specified in Day 2, resolves to the default dev user.
    """
    owner_id = project_in.owner_id
    if owner_id is not None:
        owner = db.get(User, owner_id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id {owner_id} does not exist.",
            )
    else:
        default_user = get_or_create_default_user(db)
        owner_id = default_user.id

    project = Project(
        name=project_in.name.strip(),
        description=project_in.description.strip() if project_in.description else None,
        owner_id=owner_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
):
    """List all projects."""
    return db.query(Project).order_by(Project.id.asc()).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Get a project by ID."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an existing project."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )

    update_data = project_in.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] is not None:
        project.name = update_data["name"].strip()
    if "description" in update_data:
        project.description = (
            update_data["description"].strip()
            if update_data["description"] is not None
            else None
        )

    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Delete a project by ID (cascades to all associated tasks)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )

    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
