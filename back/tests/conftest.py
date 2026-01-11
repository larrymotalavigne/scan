"""
Pytest configuration and shared fixtures.

This module provides fixtures for testing with real database
using testcontainers and mocked external services.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from back.shared.core.database import Base


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create event loop for async tests.

    Yields:
        Event loop for the test session.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container() -> Generator:
    """
    Start PostgreSQL test container.

    Yields:
        PostgreSQL container instance.
    """
    with PostgresContainer("postgres:18-alpine") as postgres:
        yield postgres


@pytest_asyncio.fixture
async def db_engine(postgres_container):
    """
    Create test database engine.

    Args:
        postgres_container: PostgreSQL container fixture.

    Yields:
        SQLAlchemy async engine.
    """
    # Get connection URL and convert to asyncpg
    connection_url = postgres_container.get_connection_url()
    async_url = connection_url.replace("psycopg2", "asyncpg")

    engine = create_async_engine(async_url, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create database session for tests.

    Args:
        db_engine: Database engine fixture.

    Yields:
        Database session for test.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker

    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_email_service(monkeypatch):
    """
    Mock email service for tests.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        List of emails sent during test.
    """
    emails_sent = []

    async def mock_send_email(to: str, subject: str, body: str) -> None:
        """Mock send email function."""
        emails_sent.append({"to": to, "subject": subject, "body": body})

    # Uncomment when email service is implemented
    # monkeypatch.setattr("back.api.services.email_service.send_email", mock_send_email)

    return emails_sent


@pytest.fixture
def sample_user_data():
    """
    Sample user data for tests.

    Returns:
        Dictionary with sample user data.
    """
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePassword123!",
        "full_name": "Test User",
    }
