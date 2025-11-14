from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    PendingWorkersView,
    ApproveWorkerView,
    PromoteToAdminView,
    AllUsersView,
    CurrentUserView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    
    # Admin - User Management
    path('pending/', PendingWorkersView.as_view(), name='pending_workers'),
    path('approve/', ApproveWorkerView.as_view(), name='approve_worker'),
    path('promote/', PromoteToAdminView.as_view(), name='promote_to_admin'),
    path('all/', AllUsersView.as_view(), name='all_users'),
]