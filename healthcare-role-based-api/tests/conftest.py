import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Load .env.test before importing anything else that relies on settings
load_dotenv(".env.test", override=True)

from app.main import app
from app.database import get_db
from app.config import settings
from app.models import Base, User, Patient, UserRole
from app.utils import hash_password

# Use the test database URL loaded from .env.test
TEST_DATABASE_URL = settings.DATABASE_URL.split("?")[0]

test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False,
    connect_args={"server_settings": {"search_path": "test_schema"}}
)
TestAsyncSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create tables in test schema before tests, drop after."""
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS test_schema"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def admin_token(client: AsyncClient, db_session: AsyncSession):
    admin = User(email="admin@test.com", password_hash=hash_password("Admin@1234"), role=UserRole.ADMIN)
    db_session.add(admin)
    await db_session.commit()
    response = await client.post("/auth/login", json={"email": "admin@test.com", "password": "Admin@1234"})
    return response.json()["access_token"]

@pytest.fixture
async def clinician_token(client: AsyncClient, db_session: AsyncSession):
    clinician = User(email="clinician@test.com", password_hash=hash_password("Clinician@123"), role=UserRole.CLINICIAN)
    db_session.add(clinician)
    await db_session.commit()
    response = await client.post("/auth/login", json={"email": "clinician@test.com", "password": "Clinician@123"})
    return response.json()["access_token"]

@pytest.fixture
async def patient_token(client: AsyncClient):
    reg_data = {
        "email": "patient@test.com",
        "password": "Patient@123",
        "name": "Test Patient",
        "age": 25,
        "gender": "Female",
        "contact": "1234567890"
    }
    await client.post("/patients", json=reg_data)
    response = await client.post("/auth/login", json={"email": "patient@test.com", "password": "Patient@123"})
    return response.json()["access_token"]
