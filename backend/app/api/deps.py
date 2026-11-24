from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User


def get_or_create_default_user(db: Session = Depends(get_db)) -> User:
    """
    Day 2 development helper: returns an existing user or creates a default
    seed user when owner_id is omitted. In Day 3, this will be replaced by
    JWT authentication middleware (`get_current_user`).
    """
    user = db.query(User).first()
    if not user:
        user = User(
            email="dev@sprintflow.local",
            password_hash="dev_insecure_placeholder_day2",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
