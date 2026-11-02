import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import Base, get_db
from app.main import app


engine = create_engine(settings.test_database_url)

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client(client):
    client.post("/auth/register", json={"email": "owner@example.com", "password": "correct-password"})
    r = client.post("/auth/login", data={"username": "owner@example.com", "password": "correct-password"})
    client.headers["Authorization"] = f"Bearer {r.json()["access_token"]}"
    return client


