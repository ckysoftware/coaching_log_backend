from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_active_user, User

from typing import Optional, List
from pydantic import BaseModel

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.api import models

from datetime import datetime, timezone


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


router = APIRouter()

CURRENT_COACHING_LOG_VERSION = "1.1"


class CoachingLogData(BaseModel):
    ansDate: str
    ansSessionFormat: Optional[str]
    ansMeetingVenue: Optional[str]
    ansSessionDuration: Optional[str]
    ansQ1Introduction: Optional[str]
    ansQ2Dermatology: Optional[str]
    ansQ3Pharmacology: Optional[str]
    ansQ4Nutrition: Optional[str]
    ansQ5Stress: Optional[str]
    ansQ6Sleep: Optional[str]
    ansQ7Exercise: Optional[str]
    ansQ8Environment: Optional[str]
    ansQ9Others: Optional[str]


class CoachingLog(BaseModel):
    version: str
    data: CoachingLogData
    locked: bool
    created_by: str
    created_at: datetime
    edited_by: str
    edited_at: datetime


class Message(BaseModel):
    message: str


@router.get("/list/{client_id}", response_model=List[CoachingLog])
async def list_all_coaching_logs(
    client_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> list[CoachingLog]:
    """List all coaching_logs of this client_id if the current_user is his/her coach or admin"""

    client = db.query(models.Clients).filter_by(id=client_id).first()
    if client and (
        client.coach_username == current_user.username or current_user.role == "admin"
    ):
        coaching_logs = []
        for coaching_log in client.coaching_logs_list:
            coaching_logs.append(coaching_log.__dict__)
        return coaching_logs
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/create/{client_id}", response_model=Message)
async def create_coaching_log(
    client_id: str,
    coaching_log_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Create a new coaching log for this client_id, and lock the last coaching log.
    Then, create a new coaching_log_reimbursement for this coaching log.
    Admin cannot create coaching log for clients.
    """

    client = db.query(models.Clients).filter_by(id=client_id).first()
    if client and client.coach_username == current_user.username:
        new_coaching_log = models.Coaching_logs(
            client_id=client_id,
            version=CURRENT_COACHING_LOG_VERSION,
            data=coaching_log_data,
            created_by=current_user.username,
            edited_by=current_user.username,
        )
        db.add(new_coaching_log)

        if len(client.coaching_logs_list) != 0:
            last_coaching_log = client.coaching_logs_list[-1]
            last_coaching_log.locked = True
        db.flush()  # get new coaching_log_id

        new_reimbursement = models.Coaching_log_reimbursement(
            coaching_log_id=new_coaching_log.id,
            reimbursed_to=current_user.username,
        )
        db.add(new_reimbursement)
        db.commit()

        return {"message": "Successfully created coaching log"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.put("/edit/{client_id}", response_model=Message)
async def edit_coaching_log(
    client_id: str,
    coaching_log_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Edit the last coaching log if it is not locked. Admin cannot edit coaching log for clients."""

    client = db.query(models.Clients).filter_by(id=client_id).first()
    if client and client.coach_username == current_user.username:
        if len(client.coaching_logs_list) != 0:
            last_coaching_log = client.coaching_logs_list[-1]
            if not last_coaching_log.locked:
                last_coaching_log.version = (
                    CURRENT_COACHING_LOG_VERSION  # forcely update new edit to current version
                )
                last_coaching_log.data = coaching_log_data
                last_coaching_log.edited_by = current_user.username
                last_coaching_log.edited_at = datetime.now(timezone.utc)
                db.commit()
                return {"message": "Successfully edited coaching log"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accessing locked files",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=404,
                detail="Coaching log not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )
