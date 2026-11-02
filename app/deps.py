from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.db import DBSession
from app.models import User, Image
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession) -> User:
    error = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authentication": "Bearer"}
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise error
    user = db.get(User, user_id)
    if user is None:
        raise error
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]


def get_own_image(image_id: int, db: DBSession, user: CurrentUser) -> Image:
    image = db.get(Image, image_id)
    if image is None or image.owner_id != user.id:
        raise HTTPException(404, "Image not found")    
    return image

OwnImage = Annotated[Image, Depends(get_own_image)]
