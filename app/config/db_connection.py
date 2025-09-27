import os
import importlib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config.main_config import Config

# Base model
Base = declarative_base()

# ✅ PostgreSQL Async Database URL
# Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DB_NAME
DATABASE_URL = (
    f"postgresql+asyncpg://{Config.DB_USER}:{Config.DB_PASS}"
    f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
)

# ✅ Create Async Engine for PostgreSQL
# Allow up to 60 connections (40 base pool + 20 overflow)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=40,        # default number of persistent connections
    max_overflow=20,     # extra connections allowed beyond pool_size
    pool_recycle=600,    # recycle every 10 min
    pool_timeout=30,     # timeout if pool is full
    pool_pre_ping=True,  # health check
    future=True
)

# ✅ Create Async Session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ✅ Dependency for DB session
async def get_db():
    """Provide a database session with proper exception handling."""
    async with AsyncSessionLocal() as session:
        try:
            yield session  # Provide session for DB operations
        except SQLAlchemyError as e:
            print(f"Database Error: {e}")  # Replace with proper logging
            await session.rollback()
        finally:
            await session.close()

