from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import TaskPriority, TaskStatus

if TYPE_CHECKING:
    from app.models.project import Project


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, values_callable=lambda obj: [e.value for e in obj], native_enum=False),
        default=TaskStatus.TODO,
        nullable=False,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, values_callable=lambda obj: [e.value for e in obj], native_enum=False),
        default=TaskPriority.MEDIUM,
        nullable=False,
        index=True,
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
