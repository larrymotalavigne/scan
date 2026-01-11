"""
Integration tests for user controller.

Tests controller and database layer interaction with real database.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from back.api.controllers import user_controller
from back.api.schemas.user_schemas import UserCreate, UserUpdate


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserController:
    """Test user controller with real database."""

    async def test_create_user_success(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test creating a new user successfully."""
        user_data = UserCreate(**sample_user_data)
        user = await user_controller.create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.username == sample_user_data["username"]
        assert user.full_name == sample_user_data["full_name"]
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.hashed_password != sample_user_data["password"]

    async def test_create_user_duplicate_email(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test creating user with duplicate email fails."""
        user_data = UserCreate(**sample_user_data)

        # Create first user
        await user_controller.create_user(db_session, user_data)

        # Try to create second user with same email
        with pytest.raises(ValueError, match="Email already registered"):
            await user_controller.create_user(db_session, user_data)

    async def test_create_user_duplicate_username(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test creating user with duplicate username fails."""
        user_data = UserCreate(**sample_user_data)

        # Create first user
        await user_controller.create_user(db_session, user_data)

        # Try to create second user with same username but different email
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        user_data2 = UserCreate(**duplicate_data)

        with pytest.raises(ValueError, match="Username already taken"):
            await user_controller.create_user(db_session, user_data2)

    async def test_get_user_by_id_success(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test getting user by ID successfully."""
        user_data = UserCreate(**sample_user_data)
        created_user = await user_controller.create_user(db_session, user_data)

        retrieved_user = await user_controller.get_user_by_id(
            db_session, created_user.id
        )

        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    async def test_get_user_by_id_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user raises error."""
        with pytest.raises(ValueError, match="User not found"):
            await user_controller.get_user_by_id(db_session, 99999)

    async def test_update_user_success(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test updating user successfully."""
        user_data = UserCreate(**sample_user_data)
        user = await user_controller.create_user(db_session, user_data)

        update_data = UserUpdate(full_name="Updated Name")
        updated_user = await user_controller.update_user(
            db_session, user.id, update_data
        )

        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == user.email  # Unchanged

    async def test_update_user_duplicate_email(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test updating user with duplicate email fails."""
        # Create first user
        user_data1 = UserCreate(**sample_user_data)
        user1 = await user_controller.create_user(db_session, user_data1)

        # Create second user
        user_data2_dict = sample_user_data.copy()
        user_data2_dict["email"] = "user2@example.com"
        user_data2_dict["username"] = "user2"
        user_data2 = UserCreate(**user_data2_dict)
        user2 = await user_controller.create_user(db_session, user_data2)

        # Try to update user2 email to user1 email
        update_data = UserUpdate(email=user1.email)
        with pytest.raises(ValueError, match="Email already registered"):
            await user_controller.update_user(db_session, user2.id, update_data)

    async def test_authenticate_user_success(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test authenticating user with correct credentials."""
        user_data = UserCreate(**sample_user_data)
        await user_controller.create_user(db_session, user_data)

        authenticated = await user_controller.authenticate_user(
            db_session,
            sample_user_data["username"],
            sample_user_data["password"],
        )

        assert authenticated is not None
        assert authenticated.username == sample_user_data["username"]

    async def test_authenticate_user_with_email(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test authenticating user with email instead of username."""
        user_data = UserCreate(**sample_user_data)
        await user_controller.create_user(db_session, user_data)

        authenticated = await user_controller.authenticate_user(
            db_session, sample_user_data["email"], sample_user_data["password"]
        )

        assert authenticated is not None
        assert authenticated.email == sample_user_data["email"]

    async def test_authenticate_user_wrong_password(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test authentication fails with wrong password."""
        user_data = UserCreate(**sample_user_data)
        await user_controller.create_user(db_session, user_data)

        authenticated = await user_controller.authenticate_user(
            db_session, sample_user_data["username"], "WrongPassword"
        )

        assert authenticated is None

    async def test_delete_user_success(
        self, db_session: AsyncSession, sample_user_data: dict
    ):
        """Test deleting user successfully."""
        user_data = UserCreate(**sample_user_data)
        user = await user_controller.create_user(db_session, user_data)

        await user_controller.delete_user(db_session, user.id)

        with pytest.raises(ValueError, match="User not found"):
            await user_controller.get_user_by_id(db_session, user.id)
