from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.api.auth import User, get_current_active_user, verify_is_admin

from typing import Optional, List
from pydantic import BaseModel

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.api import models

import random
import json

router = APIRouter()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class ClientName(BaseModel):
    first_name: str
    last_name: str
    id: int


class CoachName(BaseModel):
    first_name: str
    last_name: str


class ClientCoachName(BaseModel):
    """Client name & id + coach name"""

    client_details: ClientName
    coach_details: CoachName


class ClientDetails(ClientName):
    coach_username: Optional[str]
    email: str
    mobile_phone: str
    sex: str
    age: int
    current_location: str


def generate_client_id() -> int:
    """generate random client_id (int) [0, 999999], collision isn't handled"""

    new_id = random.randint(0, 999999)
    return new_id


@router.get("/list", response_model=List[ClientName])
async def list_accessible_clients(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
) -> list[ClientName]:
    """list all the clients this User has access to"""

    clients_list = (
        db.query(models.Users)
        .filter_by(username=current_user.username)
        .first()
        .clients_list
    )

    clients = []
    for client in clients_list:
        clients.append(client.__dict__)
    return clients


@router.get("/details/{client_id}", response_model=ClientCoachName)
async def list_client_details(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ClientCoachName:
    """list client's details by cilent_id. Only allows admin or client's coach to access"""

    client = db.query(models.Clients).filter_by(id=client_id).first()
    if client and (
        client.coach_username == current_user.username or current_user.role == "admin"
    ):
        if current_user.role == "admin":
            # only need to query coach name if user is admin
            coach = (
                db.query(models.Users).filter_by(username=client.coach_username).first()
            )
            if coach:
                coach_details = coach.__dict__  # the user is admin but not the coach
            else:
                coach_details = {
                    "first_name": "UNASSIGNED",
                    "last_name": "",
                }  # no coach
        else:
            coach_details = current_user  # the user is the coach

        client_details = {
            "client_details": client.__dict__,
            "coach_details": coach_details,
        }
        return client_details
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )


### ---------- admin right ----------
@router.post("/create")
async def create_client(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    mobile_phone: str = Form(...),
    sex: str = Form(...),
    age: str = Form(...),
    current_location: str = Form(...),
    dq: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_is_admin),
) -> dict[str, int]:
    """create a new client and returns the client_id. Only admin can access"""
    age = int(age)
    client_id = generate_client_id()

    # Collision test
    while db.query(models.Clients.id).filter_by(id=client_id).first() is not None:
        client_id = generate_client_id()

    dq = json.loads(dq)  # 2D list type, [0]: question, [1]: answer

    new_client = models.Clients(
        id=client_id,
        coach_username=None,
        first_name=first_name,
        last_name=last_name,
        email=email,
        mobile_phone=mobile_phone,
        sex=sex,
        age=age,
        current_location=current_location,
        created_by=current_user.username,
    )

    new_dq = models.Client_discovery_questionnaire(
        client_id=client_id,
        version="1.1",
        data=dq,
    )

    db.add(new_client)
    db.flush()  # generate new client_id
    db.add(new_dq)
    db.commit()

    return {"client_id": client_id}


@router.post(
    "/assign-coach",
    dependencies=[Depends(verify_is_admin)],
    response_model=ClientCoachName,
)
async def assign_coach_to_client(
    coach_username: str = Form(...),
    client_id: str = Form(...),
    db: Session = Depends(get_db),
) -> ClientCoachName:
    """Assign the coach to the given client by coach_username and client_id. Only admin can access"""

    # will not show error if the new coach is the same as the current coach
    coach = db.query(models.Users).filter_by(username=coach_username).first()
    client = db.query(models.Clients).filter_by(id=client_id).first()
    if coach is None:
        raise HTTPException(
            status_code=404,
            detail="Username not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client ID not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    client.coach_username = coach.username
    client_details = dict(client.__dict__)
    coach_details = dict(coach.__dict__)
    db.commit()

    return {
        "client_details": client_details,
        "coach_details": coach_details,
    }


@router.get(
    "/list-all",
    dependencies=[Depends(verify_is_admin)],
    response_model=List[ClientDetails],
)
async def list_all_clients(
    limit: int = -1, skip: int = 0, db: Session = Depends(get_db)
) -> list[ClientDetails]:
    """list all the clients in the database. Only admin can access"""

    if limit == -1:  # temporary fix to query the whole table
        clients_list = db.query(models.Clients).order_by(models.Clients.id).all()
    else:
        clients_list = db.query(models.Clients).limit(limit).offset(skip)
    clients = []
    for client in clients_list:
        clients.append(client.__dict__)
    return clients
