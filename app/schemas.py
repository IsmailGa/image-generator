from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr , Field

Kind = Literal["noise", "gradient"]

class ImageCreate(BaseModel):
    width: int = Field(256, ge=1, le=1024)
    height: int = Field(256, ge=1, le=1024)
    seed: int | None = Field(None, ge=0, lt=2**31)
    kind: Kind = "noise"

class ImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    width: int
    height: int
    seed: int
    kind: Kind
    created_at: datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
