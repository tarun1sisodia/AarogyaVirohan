"""
Seed script to populate initial admin and clinician user accounts.
Useful for testing the role-based access control locally.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine
from app.models import Base, User, UserRole
from app.utils import hash_password

async def create_demo_users():
    """Creates an admin and a clinician user if they don't exist."""
    async with AsyncSessionLocal() as session:
        # Note: In production, password generation should be more secure and possibly emailed to users.
        admin = User(
            email="admin@clinic.com",
            password_hash=hash_password("Admin@1234"),
            role=UserRole.ADMIN,
        )
        clinician = User(
            email="clinician@clinic.com",
            password_hash=hash_password("Clinician@1234"),
            role=UserRole.CLINICIAN,
        )
        
        session.add_all([admin, clinician])
        
        try:
            await session.commit()
            print("Demo admin and clinician users created successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Users may already exist or an error occurred: {e}")

async def main():
    """Initializes the database schema and seeds users."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_demo_users()

if __name__ == "__main__":
    asyncio.run(main())
