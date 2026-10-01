import pytest
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User
from app.models.device import Device
from app.models.geofence import Geofence, GeofencePoint
from app.core.security import get_password_hash, create_access_token

TEST_DB_URL = "sqlite:///./test_geofence.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_geofence.db"):
        try:
            os.remove("./test_geofence.db")
        except Exception:
            pass


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db_session) -> User:
    admin = User(
        name="Admin Tester",
        email="admintester@example.com",
        password_hash=get_password_hash("AdminPass123"),
        role="ADMIN",
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_token(test_admin_user: User) -> str:
    return create_access_token(subject=test_admin_user.id, role=test_admin_user.role)


@pytest.fixture
def test_regular_user(db_session) -> User:
    user = User(
        name="Regular Tester",
        email="regulartester@example.com",
        password_hash=get_password_hash("UserPass123"),
        role="USER",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_regular_user: User) -> str:
    return create_access_token(subject=test_regular_user.id, role=test_regular_user.role)
