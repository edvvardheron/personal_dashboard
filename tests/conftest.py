import os

os.environ.setdefault('API_KEY', 'test_key') #before import the app

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.observation #noqa: F401
from app.core.db import Base, get_db
from app.main import app


@pytest.fixture
def db():
    # Use an in-memory SQLite database for testing
    engine = create_engine(
        'sqlite://', poolclass=StaticPool, connect_args={'check_same_thread' : False}
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield session

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()