"""
User database layer - pure SQLAlchemy queries.

This module contains all database operations for users.
NO business logic, NO external service calls, NO FastAPI imports.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from back.api.schemas.user_schemas import UserCreate, UserUpdate
from back.shared.models.user import User


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Get user by ID.

    Args:
        db: Database session.
        user_id: User ID to lookup.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Get user by email address.

    Args:
        db: Database session.
        email: Email address to lookup.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    Get user by username.

    Args:
        db: Database session.
        username: Username to lookup.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[User]:
    """
    Get list of users with pagination.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of User objects.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user_data: UserCreate, hashed_password: str) -> User:
    """
    Insert new user into database.

    Args:
        db: Database session.
        user_data: User creation data.
        hashed_password: Already hashed password.

    Returns:
        Created User object.
    """
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession, user: User, user_data: UserUpdate
) -> User:
    """
    Update existing user in database.

    Args:
        db: Database session.
        user: User object to update.
        user_data: Update data (only provided fields).

    Returns:
        Updated User object.
    """
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    """
    Delete user from database.

    Args:
        db: Database session.
        user: User object to delete.
    """
    await db.delete(user)
    await db.flush()
