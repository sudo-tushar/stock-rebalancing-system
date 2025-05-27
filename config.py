import os
from dotenv import load_dotenv
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as SAAsyncSession
from sqlalchemy.orm import sessionmaker as sa_sessionmaker

# Load environment variables from .env file
load_dotenv(".env")

# Environment variable keys
REDIS_URI = os.getenv("VALKEY_URL")
REDIS_SECRET = os.getenv("VALKEY_PASSWORD")
PG_DSN = os.getenv("POSTGRES_URL")

# Redis singleton
_redis_instance = None

async def acquire_redis() -> AsyncRedis:
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = AsyncRedis.from_url(
            REDIS_URI,
            password=REDIS_SECRET,
            decode_responses=True
        )
    return _redis_instance

# SQLAlchemy async engine and session factory
_engine_instance = None
_session_factory = None

def obtain_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = create_async_engine(PG_DSN, echo=False, future=True)
    return _engine_instance

def obtain_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sa_sessionmaker(
            bind=obtain_engine(),
            class_=SAAsyncSession,
            expire_on_commit=False,
        )
    return _session_factory

# Example usage for manual session (not for FastAPI endpoints):
# async def example():
#     session_factory = obtain_session_factory()
#     async with session_factory() as session:
#         ...