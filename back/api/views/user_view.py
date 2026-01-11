"""
User views - HTTP request/response handling.

This module defines FastAPI routes for user management.
ONLY HTTP concerns - delegates all business logic to controllers.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from back.api.controllers import user_controller
from back.api.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from back.shared.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Register a new user account with email, username, and password.",
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Create a new user account.

    Args:
        user_data: User creation data (email, username, password).
        db: Database session dependency.

    Returns:
        Created user information.

    Raises:
        HTTPException: If email or username already exists.
    """
    try:
        user = await user_controller.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve user information by user ID.",
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Get user by ID.

    Args:
        user_id: User ID to retrieve.
        db: Database session dependency.

    Returns:
        User information.

    Raises:
        HTTPException: If user not found.
    """
    try:
        user = await user_controller.get_user_by_id(db, user_id)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List users",
    description="Get paginated list of users.",
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    """
    List users with pagination.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        db: Database session dependency.

    Returns:
        List of users.
    """
    users = await user_controller.get_users(db, skip, limit)
    return [UserResponse.model_validate(user) for user in users]


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information (partial update).",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update user information.

    Args:
        user_id: User ID to update.
        user_data: Update data (only provided fields will be updated).
        db: Database session dependency.

    Returns:
        Updated user information.

    Raises:
        HTTPException: If user not found or validation fails.
    """
    try:
        user = await user_controller.update_user(db, user_id, user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account.",
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete user account.

    Args:
        user_id: User ID to delete.
        db: Database session dependency.

    Raises:
        HTTPException: If user not found or cannot be deleted.
    """
    try:
        await user_controller.delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
