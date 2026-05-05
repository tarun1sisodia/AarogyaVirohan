import pytest
from httpx import AsyncClient
from app.models import User, UserRole
from app.utils import hash_password

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session):
    user = User(email="login@test.com", password_hash=hash_password("Secure!123"), role=UserRole.PATIENT)
    db_session.add(user)
    await db_session.commit()

    response = await client.post("/auth/login", json={"email": "login@test.com", "password": "Secure!123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post("/auth/login", json={"email": "nonexist@test.com", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
