"""
Database configuration and session management.
Utilizes asynchronous SQLAlchemy connection for optimal performance.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

# Create the asynchronous engine connected to our Postgres DB
# Set echo=False for production to avoid leaking queries in logs
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Session local factory for creating async sessions on demand
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    """
    FastAPI dependency that yields an asynchronous database session.
    Automatically manages session lifecycle (closing after use).
    """
    async with AsyncSessionLocal() as session:
        yield session
