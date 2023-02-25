from fastapi import APIRouter

from app.api import auth
from app.api.endpoints import (
    users,
    coaching_log,
    clients,
    settings,
)

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

api_router.include_router(users.router, prefix="/users", tags=["User"])

api_router.include_router(
    coaching_log.router, prefix="/coaching-log", tags=["Coaching-log"]
)

api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])

api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
