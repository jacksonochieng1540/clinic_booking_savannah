from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import UserActivityLog, UserProfile

User = get_user_model()


class AccountsTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123!",
            "password2": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890",
            "role": "patient",
        }

        self.test_user = User.objects.create_user(
            email="login@example.com",
            username="loginuser",
            password="LoginPass123!",
            first_name="Login",
            last_name="User",
            role="patient",
        )
        UserProfile.objects.create(user=self.test_user)

    def test_register_user_success(self):
        """Test successful user registration"""
        url = reverse("api-register")
        response = self.client.post(url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], "test@example.com")

    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        # First registration
        self.client.post(reverse("api-register"), self.user_data, format="json")

        # Second registration with same email but different username
        data = self.user_data.copy()
        data["username"] = "testuser2"
        response = self.client.post(reverse("api-register"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check for email or username error
        self.assertTrue("email" in str(response.data) or "username" in str(response.data))

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = self.user_data.copy()
        data["password2"] = "DifferentPass123!"

        response = self.client.post(reverse("api-register"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", str(response.data))

    def test_login_success(self):
        """Test successful login"""
        url = reverse("api-login")
        data = {"email": "login@example.com", "password": "LoginPass123!"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertEqual(response.data["user"]["email"], "login@example.com")

    def test_login_invalid_email(self):
        """Test login with invalid email"""
        url = reverse("api-login")
        data = {"email": "nonexistent@example.com", "password": "LoginPass123!"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", str(response.data))

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        url = reverse("api-login")
        data = {"email": "login@example.com", "password": "WrongPassword123!"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", str(response.data))

    def test_logout_success(self):
        """Test successful logout"""
        # First login to get token
        login_url = reverse("api-login")
        login_data = {"email": "login@example.com", "password": "LoginPass123!"}
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["tokens"]["access"]
        refresh_token = login_response.data["tokens"]["refresh"]

        # Logout with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_url = reverse("api-logout")
        response = self.client.post(logout_url, {"refresh_token": refresh_token}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logged out successfully")

    def test_profile_view_authenticated(self):
        """Test profile view with authenticated user"""
        # Login to get token
        login_url = reverse("api-login")
        login_data = {"email": "login@example.com", "password": "LoginPass123!"}
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["tokens"]["access"]

        # Access profile with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        profile_url = reverse("api-profile")
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "login@example.com")

    def test_profile_view_unauthenticated(self):
        """Test profile view without authentication"""
        url = reverse("api-profile")
        response = self.client.get(url)

        # DRF returns 403 for unauthenticated requests with IsAuthenticated permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_password_change_success(self):
        """Test successful password change"""
        # Login to get token
        login_url = reverse("api-login")
        login_data = {"email": "login@example.com", "password": "LoginPass123!"}
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["tokens"]["access"]

        # Change password with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        change_url = reverse("api-change-password")
        data = {
            "old_password": "LoginPass123!",
            "new_password": "NewPass123!",
            "new_password2": "NewPass123!",
        }
        response = self.client.post(change_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully")

    def test_password_change_wrong_old_password(self):
        """Test password change with wrong old password"""
        # Login to get token
        login_url = reverse("api-login")
        login_data = {"email": "login@example.com", "password": "LoginPass123!"}
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["tokens"]["access"]

        # Change password with wrong old password
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        change_url = reverse("api-change-password")
        data = {
            "old_password": "WrongOldPass123!",
            "new_password": "NewPass123!",
            "new_password2": "NewPass123!",
        }
        response = self.client.post(change_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", str(response.data))

    def test_password_reset_request(self):
        """Test password reset request"""
        url = reverse("api-password-reset")
        data = {"email": "login@example.com"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password reset link sent to your email")

    def test_password_reset_request_invalid_email(self):
        """Test password reset with invalid email"""
        url = reverse("api-password-reset")
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No user found", str(response.data))

    def test_activity_log_authenticated(self):
        """Test activity log with authenticated user"""
        # Login to get token
        login_url = reverse("api-login")
        login_data = {"email": "login@example.com", "password": "LoginPass123!"}
        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["tokens"]["access"]

        # Get activity logs with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        log_url = reverse("api-activity-logs")
        response = self.client.get(log_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_activity_log_unauthenticated(self):
        """Test activity log without authentication"""
        url = reverse("api-activity-logs")
        response = self.client.get(url)

        # DRF returns 403 for unauthenticated requests
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
