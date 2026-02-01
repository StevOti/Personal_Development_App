"""
URL patterns for core app (authentication endpoints).
Week 1: JWT authentication routes.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import LogoutView, SignupView, ProfileView

app_name = "core"

urlpatterns = [
    # Authentication endpoints
    path("auth/signup/", SignupView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
]
