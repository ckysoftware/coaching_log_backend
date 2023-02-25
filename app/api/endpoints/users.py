import uuid
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session, joinedload

from app.api.auth import (
    get_current_active_user,
    get_password_hash,
    verify_is_admin,
    User,
)
from app.database import SessionLocal
from app.api import models
from app.util import convert_db_list_to_py_list
from .clients import ClientName


class UserDetails(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    role: str
    id: int
    clients_list: Optional[List[ClientName]]


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


router = APIRouter()


### ---------- admin right ----------
@router.post("/create", dependencies=[Depends(verify_is_admin)])
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    """Create a new user with random password"""

    if db.query(models.Users).filter_by(username=username).first() is not None:
        raise HTTPException(status_code=409, detail="Username exists")

    random_password = str(uuid.uuid4())[-8:]
    hashed_password = get_password_hash(random_password)

    new_user = models.Users(
        username=username,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        created_by=current_user.username,
    )

    db.add(new_user)
    db.commit()

    return {"password": random_password}


@router.get(
    "/list-all",
    dependencies=[Depends(verify_is_admin)],
    response_model=List[UserDetails],
)
async def list_all_users(
    limit: int = -1, skip: int = 0, db: Session = Depends(get_db)
) -> list[UserDetails]:
    """Return the list of all users if the curernt user is admin"""

    if limit == -1:  # temporary fix for query the whole table
        users_list = (
            db.query(models.Users)
            .options(joinedload("clients_list"))
            .order_by(models.Users.username)
            .all()
        )
    else:
        users_list = db.query(models.Users).limit(limit).offset(skip)
    users = []
    for user in users_list:
        clients_list = convert_db_list_to_py_list(user.clients_list)
        user_dict = user.__dict__
        user_dict["clients_list"] = clients_list
        users.append(user.__dict__)
    return users
