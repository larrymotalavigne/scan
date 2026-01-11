"""
Unit tests for user controller.

Tests business logic in isolation with mocked dependencies.
"""

import pytest

from back.api.controllers.user_controller import get_password_hash, verify_password


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_generates_different_hashes(self):
        """Test that same password generates different hashes (salt)."""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert len(hash1) > 50  # Bcrypt hashes are long

    def test_verify_password_with_correct_password(self):
        """Test password verification with correct password."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword!", hashed) is False

    def test_password_hash_is_not_reversible(self):
        """Test that password hash doesn't contain original password."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert password not in hashed
