from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Annotated
from fastapi import Depends

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as session:
        yield session

DBSession = Annotated[Session, Depends(get_db)]