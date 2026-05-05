"""
SQLAlchemy Models defining the database schema.
Includes User (with roles) and Patient models.
"""
import uuid
import enum
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserRole(str, enum.Enum):
    """Enumeration for user roles to enforce role-based access control."""
    ADMIN = "admin"
    CLINICIAN = "clinician"
    PATIENT = "patient"

class User(Base):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to patient; one-to-one mapping
    patient = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Patient(Base):
    """
    Patient model holding specific demographic and contact details.
    """
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship back to the user
    user = relationship("User", back_populates="patient")
