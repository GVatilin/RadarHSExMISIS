from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from sqlalchemy import create_engine


settings = get_settings()

engine = create_async_engine(
    settings.database_uri,
    echo=True,
    future=True,
    pool_size=200,
    max_overflow=0,
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

def refresh_engine() -> None:
    global engine, async_session_maker
    engine = create_async_engine(
        get_settings().database_uri,
        echo=True,
        future=True,
        pool_size=200,
        max_overflow=0,
    )
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )


def get_sync_session():
    with sessionmaker(create_engine(settings.database_uri_sync))() as session:
        yield session