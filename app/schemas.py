"""
Pydantic schemas for data validation and serialization.
"""
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import List

class PatientRegisterRequest(BaseModel):
    """Request schema for registering a new patient."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0, lt=150)
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    contact: str = Field(..., min_length=5)

    @field_validator("password")
    def password_strength(cls, v: str) -> str:
        """
        Validates password strength:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

class PatientResponse(BaseModel):
    """Response schema representing a patient."""
    id: UUID
    name: str
    age: int
    gender: str
    contact: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Response schema for successful authentication, returning a JWT."""
    access_token: str
    token_type: str = "bearer"

class PatientListResponse(BaseModel):
    """Response schema containing a list of patients."""
    patients: List[PatientResponse]
