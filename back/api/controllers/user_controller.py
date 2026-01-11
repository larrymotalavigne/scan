"""
User controller - business logic layer.

This module contains all business logic for user operations.
NO FastAPI imports - framework-agnostic pure functions.
"""

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from back.api.database import user_database
from back.api.schemas.user_schemas import UserCreate, UserUpdate
from back.shared.models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password.
        hashed_password: Hashed password from database.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.

    Args:
        password: Plain text password.

    Returns:
        Hashed password string.
    """
    return pwd_context.hash(password)


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """
    Authenticate a user with username and password.

    Business rule: Check username or email for login.

    Args:
        db: Database session.
        username: Username or email.
        password: Plain text password.

    Returns:
        User object if authenticated, None otherwise.
    """
    # Try username first
    user = await user_database.get_user_by_username(db, username)

    # Try email if username not found
    if not user:
        user = await user_database.get_user_by_email(db, username)

    # Verify password
    if not user or not verify_password(password, user.hashed_password):
        return None

    # Check if user is active
    if not user.is_active:
        return None

    return user


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user with business logic.

    Business rules:
    - Email must be unique
    - Username must be unique
    - Password must be hashed
    - User is active by default

    Args:
        db: Database session.
        user_data: User creation data.

    Returns:
        Created User object.

    Raises:
        ValueError: If email or username already exists.
    """
    # Check if email already exists
    existing_user = await user_database.get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("Email already registered")

    # Check if username already exists
    existing_user = await user_database.get_user_by_username(db, user_data.username)
    if existing_user:
        raise ValueError("Username already taken")

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user in database
    user = await user_database.create_user(db, user_data, hashed_password)

    # Here you could add: send welcome email, create audit log, etc.

    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    """
    Get user by ID with business logic.

    Business rule: Raise error if user not found.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        User object.

    Raises:
        ValueError: If user not found.
    """
    user = await user_database.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
    return user


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[User]:
    """
    Get list of users with pagination.

    Business rule: Limit maximum page size to 100.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of User objects.
    """
    # Enforce maximum limit
    if limit > 100:
        limit = 100

    return await user_database.get_users(db, skip, limit)


async def update_user(
    db: AsyncSession, user_id: int, user_data: UserUpdate
) -> User:
    """
    Update user with business logic.

    Business rules:
    - User must exist
    - Email must be unique if changed
    - Cannot deactivate superuser

    Args:
        db: Database session.
        user_id: User ID to update.
        user_data: Update data.

    Returns:
        Updated User object.

    Raises:
        ValueError: If validation fails.
    """
    # Get existing user
    user = await user_database.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    # Check email uniqueness if changing
    if user_data.email and user_data.email != user.email:
        existing = await user_database.get_user_by_email(db, user_data.email)
        if existing:
            raise ValueError("Email already registered")

    # Prevent deactivating superuser
    if user_data.is_active is False and user.is_superuser:
        raise ValueError("Cannot deactivate superuser")

    # Update user
    updated_user = await user_database.update_user(db, user, user_data)

    return updated_user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    """
    Delete user with business logic.

    Business rules:
    - User must exist
    - Cannot delete superuser

    Args:
        db: Database session.
        user_id: User ID to delete.

    Raises:
        ValueError: If validation fails.
    """
    # Get user
    user = await user_database.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    # Prevent deleting superuser
    if user.is_superuser:
        raise ValueError("Cannot delete superuser")

    # Delete user
    await user_database.delete_user(db, user)
