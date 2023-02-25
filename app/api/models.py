from sqlalchemy import Column, ForeignKey
from sqlalchemy import Text, Integer, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.schema import Identity, CreateTable
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from app.database import engine

Base = declarative_base()


class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(TIMESTAMP, nullable=True, default=func.now())


class Users(Base):
    __tablename__ = "users"
    username = Column(String(255), primary_key=True)
    id = Column(Integer, Identity(start=1, increment=1), unique=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    role = Column(String(255))
    disabled = Column(Boolean, default=False)
    created_by = Column(String(255), ForeignKey("users.username"))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    clients_list = relationship(
        "Clients",
        primaryjoin="Users.username==Clients.coach_username",
        order_by="Clients.id",
    )


class Clients(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, autoincrement=False)
    coach_username = Column(String(255), ForeignKey("users.username"), index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    mobile_phone = Column(String(255))
    sex = Column(String(255))
    age = Column(Integer)
    current_location = Column(String(255))
    disabled = Column(Boolean, default=False)
    created_by = Column(String(255), ForeignKey("users.username"))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    coaching_logs_list = relationship(
        "Coaching_logs", order_by="Coaching_logs.created_at"
    )


class Coaching_logs(Base):
    __tablename__ = "coaching_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), index=True)
    version = Column(String(255))
    data = Column(JSON)
    locked = Column(Boolean, default=False)
    created_by = Column(String(255), ForeignKey("users.username"), index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    edited_by = Column(String(255), ForeignKey("users.username"), index=True)
    edited_at = Column(TIMESTAMP(timezone=True), default=func.now())


class Client_discovery_questionnaire(Base):
    __tablename__ = "client_discovery_questionnaire"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), index=True)
    version = Column(String(255))
    data = Column(ARRAY(Text, dimensions=2))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())


class Coaching_log_reimbursement(Base):
    __tablename__ = "coaching_log_reimbursement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    coaching_log_id = Column(Integer, ForeignKey("coaching_logs.id"), index=True)
    reimbursed = Column(Boolean, default=False)
    reimbursed_to = Column(String(255), ForeignKey("users.username"), index=True)
    reimbursed_at = Column(TIMESTAMP(timezone=True), default=None)
    reimbursed_via = Column(String(255), default=None)


def print_tables():
    print(CreateTable(Users.__table__).compile(engine))
    print(CreateTable(Clients.__table__).compile(engine))
    print(CreateTable(Coaching_logs.__table__).compile(engine))
    print(CreateTable(Client_discovery_questionnaire.__table__).compile(engine))
    print(CreateTable(Coaching_log_reimbursement.__table__).compile(engine))
