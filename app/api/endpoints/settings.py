from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session

from app.api.auth import (
    User,
    get_current_active_user,
    get_password_hash,
    authenticate_user,
)
from app.database import SessionLocal
from app.api import models

router = APIRouter()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Change password for current user if the current password is correct"""

    user_in_db = authenticate_user(current_user.username, current_password)
    if user_in_db:
        hashed_new_password = get_password_hash(new_password)
        user = db.query(models.Users).filter_by(username=current_user.username).first()
        user.hashed_password = hashed_new_password
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "Successfully changed password"}
