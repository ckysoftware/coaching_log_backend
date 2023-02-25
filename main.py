from fastapi import FastAPI

from app.api.router import api_router
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(".env")

app = FastAPI()


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["0.0.0.0", "54.255.119.31", "http://54.255.119.31",
                   "http://coach.wederm.hk", "coach.wederm.hk", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
