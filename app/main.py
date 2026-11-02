import random

from fastapi import FastAPI, Query, Response
from sqlalchemy import select
from typing import Annotated

from app.db import DBSession
from app.generator import render_image
from app.models import Image
from app.schemas import ImageCreate, ImageRead
from app.deps import OwnImage, CurrentUser

from app.routers import auth


app = FastAPI()

@app.post("/images", response_model=ImageRead, status_code=201)
def create_image(data: ImageCreate, db: DBSession, user: CurrentUser):
    seed = data.seed if data.seed is not None else random.randrange(2**31)
    image = Image(width=data.width, height=data.height, seed=seed, kind=data.kind, owner_id=user.id)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

@app.get("/images", response_model=list[ImageRead])
def list_images(
    db: DBSession,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = (
        select(Image)
        .where(Image.owner_id == user.id)
        .order_by(Image.id.desc())
        .limit(limit)
        .offset(offset)
        )
    return db.scalars(stmt).all()


@app.get("/images/{image_id}", response_model=ImageRead)
def get_image_meta(image: OwnImage):
    return image


@app.get("/images/{image_id}/file")
def get_image_file(image: OwnImage):
    png = render_image(image.width, image.height, image.seed, image.kind)
    return Response(png, media_type="image/png")

@app.get("/health")
def get_health_check():
    return {"status": "ok"}

app.include_router(auth.router)
