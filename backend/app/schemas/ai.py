from pydantic import BaseModel, ConfigDict, Field


class SubtaskItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Actionable title for the subtask")
    description: str | None = Field(default=None, max_length=1000, description="Brief description or acceptance criteria")


class SubtaskSuggestionResponse(BaseModel):
    task_id: int
    task_title: str
    subtasks: list[SubtaskItem] = Field(..., min_length=1, max_length=8, description="1 to 8 structured subtasks")

    model_config = ConfigDict(from_attributes=True)


class BatchTaskCreate(BaseModel):
    project_id: int
    tasks: list[SubtaskItem] = Field(..., min_length=1, max_length=20)
