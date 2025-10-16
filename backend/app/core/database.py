# app/core/database.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine with proper pooling
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    pool_recycle=3600,  # Recycle connections after 1 hour
    poolclass=None if "sqlite" not in str(settings.DATABASE_URL) else NullPool,
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
