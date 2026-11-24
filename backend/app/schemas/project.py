from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(default=None, description="Optional project description")


class ProjectCreate(ProjectBase):
    # Optional in Day 2: if omitted, a default development user is assigned.
    # In Day 3, this will be strictly populated by JWT authenticated user.
    owner_id: int | None = Field(default=None, description="Optional owner user ID for Day 2")


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255, description="Updated project name")
    description: str | None = Field(default=None, description="Updated project description")


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
