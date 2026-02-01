"""
Unit tests for core models (User, UserProfile).
Week 1: Tests for user creation, authentication, and profile.
"""

import pytest
from django.contrib.auth import get_user_model

from core.models import UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality."""

    def test_create_user(self):
        """Test creating a user with valid data."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        assert admin_user.is_staff
        assert admin_user.is_superuser
        assert admin_user.is_active

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        assert str(user) == "testuser"


@pytest.mark.django_db
class TestUserProfile:
    """Test UserProfile model functionality."""

    def test_profile_auto_created_on_user_creation(self):
        """Test that profile is automatically created when user is created."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        # Profile should be auto-created via signal
        assert hasattr(user, "profile")
        assert UserProfile.objects.filter(user=user).exists()

    def test_profile_default_values(self):
        """Test profile has correct default values."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        profile = user.profile
        assert profile.target_identity == ""
        assert profile.onboarding_completed is False

    def test_profile_str_representation(self):
        """Test profile string representation."""
        user = User.objects.create_user(username="testuser")
        profile = user.profile
        assert str(profile) == "testuser's profile"

    def test_update_profile(self):
        """Test updating profile fields."""
        user = User.objects.create_user(username="testuser", email="test@example.com")
        profile = user.profile
        profile.target_identity = "A healthy person who exercises daily"
        profile.onboarding_completed = True
        profile.save()

        # Refresh from database
        profile.refresh_from_db()
        assert profile.target_identity == "A healthy person who exercises daily"
        assert profile.onboarding_completed is True
