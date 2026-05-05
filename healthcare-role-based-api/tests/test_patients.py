import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_patient_success(client: AsyncClient):
    data = {
        "email": "newpatient@example.com",
        "password": "Strong!123",
        "name": "John Doe",
        "age": 35,
        "gender": "Male",
        "contact": "+11234567890"
    }
    response = await client.post("/patients", json=data)
    assert response.status_code == 201
    res = response.json()
    assert res["email"] == data["email"]
    assert res["name"] == data["name"]
    assert "id" in res

@pytest.mark.asyncio
async def test_register_patient_duplicate_email(client: AsyncClient):
    data = {
        "email": "duplicate@example.com",
        "password": "Strong!123",
        "name": "Jane",
        "age": 30,
        "gender": "Female",
        "contact": "999000000"
    }
    await client.post("/patients", json=data)
    response = await client.post("/patients", json=data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_register_patient_missing_field(client: AsyncClient):
    data = {
        "email": "missing@example.com",
        "password": "Strong!123",
        "name": "Missing",
        "gender": "Male",
        "contact": "111000"
    }
    response = await client.post("/patients", json=data)
    assert response.status_code == 422 

@pytest.mark.asyncio
async def test_list_patients_admin_allowed(client: AsyncClient, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await client.get("/patients?skip=0&limit=10", headers=headers)
    assert response.status_code == 200
    assert "patients" in response.json()

@pytest.mark.asyncio
async def test_list_patients_clinician_allowed(client: AsyncClient, clinician_token):
    headers = {"Authorization": f"Bearer {clinician_token}"}
    response = await client.get("/patients", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_patients_patient_forbidden(client: AsyncClient, patient_token):
    headers = {"Authorization": f"Bearer {patient_token}"}
    response = await client.get("/patients", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden: Patients cannot access this resource"

@pytest.mark.asyncio
async def test_list_patients_no_token(client: AsyncClient):
    response = await client.get("/patients")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_patients_invalid_token(client: AsyncClient):
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = await client.get("/patients", headers=headers)
    assert response.status_code == 401
