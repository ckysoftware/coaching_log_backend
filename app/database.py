import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv(".env")
engine = create_engine(
    "postgresql://{}:{}@{}:{}/{}".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PASSWORD"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
        os.environ.get("DB_DBNAME"),
    )
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
