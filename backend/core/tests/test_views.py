"""
Unit tests for core views (authentication endpoints).
Week 1: Tests for signup, login, refresh, logout endpoints.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestSignupView:
    """Test user registration endpoint."""

    def test_signup_successful(self):
        """Test successful user registration."""
        client = APIClient()
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["username"] == "newuser"

        # Verify user was created in database
        assert User.objects.filter(username="newuser").exists()

    def test_signup_password_mismatch(self):
        """Test registration fails with mismatched passwords."""
        client = APIClient()
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123",
            "password2": "differentpass",
        }
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username="newuser").exists()

    def test_signup_duplicate_username(self):
        """Test registration fails with duplicate username."""
        User.objects.create_user(username="existinguser", email="existing@example.com")

        client = APIClient()
        url = reverse("signup")
        data = {
            "username": "existinguser",
            "email": "newuser@example.com",
            "password": "testpass123",
            "password2": "testpass123",
        }
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data


@pytest.mark.django_db
class TestLoginView:
    """Test JWT token obtain endpoint."""

    def test_login_successful(self):
        """Test successful login with valid credentials."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = APIClient()
        url = reverse("login")
        data = {"username": "testuser", "password": "testpass123"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self):
        """Test login fails with wrong password."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = APIClient()
        url = reverse("login")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self):
        """Test login fails with non-existent user."""
        client = APIClient()
        url = reverse("login")
        data = {"username": "nonexistent", "password": "testpass123"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefreshView:
    """Test JWT token refresh endpoint."""

    def test_refresh_token_successful(self):
        """Test successful token refresh."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = APIClient()
        # Get tokens first
        login_url = reverse("login")
        login_data = {"username": "testuser", "password": "testpass123"}
        login_response = client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["refresh"]

        # Now refresh the token
        refresh_url = reverse("token_refresh")
        refresh_data = {"refresh": refresh_token}
        response = client.post(refresh_url, refresh_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data  # New refresh token due to rotation

    def test_refresh_token_invalid(self):
        """Test refresh fails with invalid token."""
        client = APIClient()
        refresh_url = reverse("token_refresh")
        refresh_data = {"refresh": "invalid_token_string"}
        response = client.post(refresh_url, refresh_data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogoutView:
    """Test logout endpoint (blacklist refresh token)."""

    def test_logout_successful(self):
        """Test successful logout (token blacklisting)."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        client = APIClient()
        # Login first
        login_url = reverse("login")
        login_data = {"username": "testuser", "password": "testpass123"}
        login_response = client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["refresh"]

        # Logout
        logout_url = reverse("logout")
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        logout_data = {"refresh": refresh_token}
        response = client.post(logout_url, logout_data, format="json")

        assert response.status_code == status.HTTP_205_RESET_CONTENT

        # Try to use the blacklisted token
        refresh_url = reverse("token_refresh")
        refresh_response = client.post(
            refresh_url, {"refresh": refresh_token}, format="json"
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_authentication(self):
        """Test logout requires authentication."""
        client = APIClient()
        logout_url = reverse("logout")
        logout_data = {"refresh": "some_token"}
        response = client.post(logout_url, logout_data, format="json")

        # Should fail without authentication
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST,
        ]


@pytest.mark.django_db
class TestProtectedEndpoint:
    """Test that endpoints require authentication."""

    def test_access_without_token(self):
        """Test that accessing protected endpoint without token fails."""
        client = APIClient()
        # This is just a test - we don't have a protected endpoint yet
        # But we can test that our JWT authentication is configured
        # For now, we'll skip this or test a future endpoint
        pass
