import random
import string

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from core.email import send_password_reset_email, send_welcome_email
from core.permissions import IsAdminUser

from .models import UserActivityLog
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    UserActivityLogSerializer,
    UserCreateSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""

    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_welcome_email(user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """User login endpoint"""

    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "message": "Login successful",
                "user": UserSerializer(serializer.validated_data["user"]).data,
                "tokens": {
                    "refresh": serializer.validated_data["refresh"],
                    "access": serializer.validated_data["access"],
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """User logout endpoint"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserLogoutSerializer

    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserActivityLog.objects.create(
            user=request.user,
            action="logout",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class TokenRefreshView(TokenRefreshView):
    """Refresh access token endpoint"""

    pass


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get/Update current user profile"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    """Change password endpoint"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class PasswordResetRequestView(generics.GenericAPIView):
    """Request password reset"""

    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        token = "".join(random.choices(string.ascii_letters + string.digits, k=50))
        user.password_reset_token = token
        user.token_created_at = timezone.now()
        user.save()
        reset_link = f"https://yourdomain.com/reset-password?token={token}"
        send_password_reset_email(user, reset_link)
        return Response(
            {
                "message": "Password reset link sent to your email",
                "token": token,
                "reset_link": reset_link,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirm password reset"""

    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        try:
            user = User.objects.get(password_reset_token=token)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.token_created_at:
            expiry_time = user.token_created_at + timezone.timedelta(hours=1)
            if timezone.now() > expiry_time:
                return Response(
                    {"error": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST
                )
        user.set_password(new_password)
        user.password_reset_token = None
        user.token_created_at = None
        user.save()
        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )


class UserActivityLogView(generics.ListAPIView):
    """Get user activity logs"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserActivityLogSerializer

    def get_queryset(self):
        return UserActivityLog.objects.filter(user=self.request.user)


class UserListView(generics.ListAPIView):
    """Admin: List all users"""

    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_fields = ["role", "is_active", "is_verified"]
    search_fields = ["email", "first_name", "last_name", "username"]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: Get/Update/Delete user"""

    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {"message": "User deactivated successfully"}, status=status.HTTP_200_OK
        )


# ==================== TEMPLATE VIEWS ====================


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"user": user})


def home_view(request):
    """Home page"""
    return render(request, "home.html")
