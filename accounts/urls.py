from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import views_dashboard

urlpatterns = [
    # API Authentication endpoints
    path('api/register/', views.RegisterView.as_view(), name='api-register'),
    path('api/login/', views.LoginView.as_view(), name='api-login'),
    path('api/logout/', views.LogoutView.as_view(), name='api-logout'),
    path('api/token/refresh/', views.TokenRefreshView.as_view(), name='api-token-refresh'),
    path('api/profile/', views.UserProfileView.as_view(), name='api-profile'),
    path('api/change-password/', views.PasswordChangeView.as_view(), name='api-change-password'),
    path('api/password-reset/', views.PasswordResetRequestView.as_view(), name='api-password-reset'),
    path('api/password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='api-password-reset-confirm'),
    path('api/activity-logs/', views.UserActivityLogView.as_view(), name='api-activity-logs'),
    path('api/admin/users/', views.UserListView.as_view(), name='api-admin-user-list'),
    path('api/admin/users/<int:id>/', views.UserDetailView.as_view(), name='api-admin-user-detail'),
    
    # Template views
    path('profile/', views.profile_view, name='profile'),
    
    # Dashboard URLs
    path('dashboard/', views_dashboard.dashboard_view, name='dashboard'),
    path('dashboard/patient/', views_dashboard.patient_dashboard, name='patient_dashboard'),
    path('dashboard/doctor/', views_dashboard.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/admin/', views_dashboard.admin_dashboard, name='admin_dashboard'),
]