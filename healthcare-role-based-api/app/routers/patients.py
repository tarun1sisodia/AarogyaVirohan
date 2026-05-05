"""
Patient endpoints.
Handles patient registration and listing (listing is protected via middleware).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import User, Patient, UserRole
from app.schemas import PatientRegisterRequest, PatientResponse, PatientListResponse
from app.utils import hash_password

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(payload: PatientRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Registers a new patient. 
    Creates a User account with the 'patient' role and an associated Patient profile.
    """
    # Check if email already exists
    existing_user = await db.execute(select(User).where(User.email == payload.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Email already registered"
        )

    # Hash password and create user
    hashed_pw = hash_password(payload.password)
    user = User(email=payload.email, password_hash=hashed_pw, role=UserRole.PATIENT)
    db.add(user)
    
    # Flush to database to obtain the auto-generated user.id
    await db.flush()

    # Create patient record linked to the new user
    patient = Patient(
        user_id=user.id,
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        contact=payload.contact,
    )
    db.add(patient)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Database integrity error")
        
    await db.refresh(patient)

    return PatientResponse(
        id=patient.id,
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        contact=patient.contact,
        email=user.email,
        created_at=patient.created_at,
    )

@router.get("", response_model=PatientListResponse)
async def list_patients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Lists patients with optional pagination. 
    Role enforcement is handled securely via RoleBasedAccessMiddleware.
    """
    stmt = (
        select(Patient, User.email)
        .join(User, Patient.user_id == User.id)
        .order_by(Patient.created_at)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    patients = []
    for patient, email in rows:
        patients.append(PatientResponse(
            id=patient.id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            contact=patient.contact,
            email=email,
            created_at=patient.created_at,
        ))
    return PatientListResponse(patients=patients)
