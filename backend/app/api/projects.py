from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new project.
    Sets owner_id strictly from the authenticated current user.
    """
    project = Project(
        name=project_in.name.strip(),
        description=project_in.description.strip() if project_in.description else None,
        owner_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all projects owned by the authenticated current user."""
    return (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.id.asc())
        .all()
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a project by ID, strictly enforcing user ownership."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project.",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Partially update an existing project, strictly enforcing user ownership."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this project.",
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project by ID, strictly enforcing user ownership."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found.",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this project.",
        )

    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
