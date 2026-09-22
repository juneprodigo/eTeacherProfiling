"""
accounts/urls.py — Authentication URL Patterns
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    MeView,
    ChangePasswordView,
    UserListCreateView,
    UserDetailUpdateDeleteView,
    DashboardStatsView,
)

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),

    # User management
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailUpdateDeleteView.as_view(), name='user-detail'),

    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
