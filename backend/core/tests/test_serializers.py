"""
Unit tests for core serializers (User, UserProfile).
Week 1: Tests for serializer validation, password hashing, etc.
"""

import pytest
from core.serializers import (
    UserProfileSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserRegisterSerializer:
    """Test UserRegisterSerializer validation and user creation."""

    def test_valid_registration_data(self):
        """Test serializer with valid registration data."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }
        serializer = UserRegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")

    def test_password_mismatch(self):
        """Test that mismatched passwords are rejected."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "differentpass",
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert (
            "password" in serializer.errors or "non_field_errors" in serializer.errors
        )

    def test_password_too_short(self):
        """Test that short passwords are rejected."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",
            "password2": "123",
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_invalid_email_format(self):
        """Test that invalid email format is rejected."""
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "testpass123",
            "password2": "testpass123",
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_duplicate_username(self):
        """Test that duplicate usernames are rejected."""
        # Create first user
        User.objects.create_user(username="testuser", email="test1@example.com")

        # Try to create another with same username
        data = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "username" in serializer.errors

    def test_duplicate_email(self):
        """Test that duplicate emails are rejected."""
        # Create first user
        User.objects.create_user(username="testuser1", email="test@example.com")

        # Try to create another with same email
        data = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestUserSerializer:
    """Test UserSerializer for read operations."""

    def test_serialize_user(self):
        """Test serializing a user object."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        serializer = UserSerializer(user)
        assert serializer.data["username"] == "testuser"
        assert serializer.data["email"] == "test@example.com"
        assert "password" not in serializer.data  # Password should not be in output


@pytest.mark.django_db
class TestUserProfileSerializer:
    """Test UserProfileSerializer."""

    def test_serialize_profile(self):
        """Test serializing a user profile."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        profile = user.profile
        profile.target_identity = "A healthy person"
        profile.onboarding_completed = True
        profile.save()

        serializer = UserProfileSerializer(profile)
        assert serializer.data["target_identity"] == "A healthy person"
        assert serializer.data["onboarding_completed"] is True

    def test_update_profile(self):
        """Test updating profile via serializer."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        profile = user.profile

        data = {"target_identity": "A productive person", "onboarding_completed": True}
        serializer = UserProfileSerializer(profile, data=data, partial=True)
        assert serializer.is_valid()
        updated_profile = serializer.save()
        assert updated_profile.target_identity == "A productive person"
        assert updated_profile.onboarding_completed is True
