from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import DBSession
from app.deps import CurrentUser
from app.models import User
from app.schemas import UserCreate, UserRead, Token
from app.security import DUMMY_HASH, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: DBSession):
    user = User(email=data.email.lower(), hashed_password=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered")
    db.refresh(user)
    return user

@router.post("/login", status_code=200)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBSession):
    user = db.scalar(select(User).where(User.email == form.username.lower()))
    if user is None:
        verify_password(form.password, DUMMY_HASH)
        raise HTTPException(401, "Incorrect email or password")
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_access_token(user.id))

@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user