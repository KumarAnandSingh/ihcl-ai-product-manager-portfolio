"""Database utilities and connection management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
import structlog

from .config import get_settings
from ..models.base import Base

logger = structlog.get_logger()

# Global engine and session factory
_engine = None
_session_factory = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,  # Use NullPool for development
            echo=settings.environment == "development",
        )
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_db_session():
    """Get a database session."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize the database by creating tables."""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


async def close_db():
    """Close database connections."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
    logger.info("Database connections closed")