from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: str | None = Field(default=None, description="Optional task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    due_date: datetime | None = Field(default=None, description="Optional task due date")


class TaskCreate(TaskBase):
    project_id: int = Field(..., description="ID of the parent project")


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255, description="Updated task title")
    description: str | None = Field(default=None, description="Updated task description")
    status: TaskStatus | None = Field(default=None, description="Updated task status")
    priority: TaskPriority | None = Field(default=None, description="Updated task priority")
    due_date: datetime | None = Field(default=None, description="Updated task due date")


class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
