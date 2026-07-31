from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import UserProfile

from .models import Patient

User = get_user_model()


class PatientsTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create admin user
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User",
            role="admin",
            is_superuser=True,
            is_staff=True,
        )
        UserProfile.objects.create(user=self.admin_user)

        # Create patient user
        self.patient_user = User.objects.create_user(
            email="patient@example.com",
            username="patientuser",
            password="PatientPass123!",
            first_name="Jane",
            last_name="Doe",
            role="patient",
        )
        UserProfile.objects.create(user=self.patient_user)

        # Create patient profile
        self.patient = Patient.objects.create(
            user=self.patient_user,
            blood_type="A+",
            allergies="Penicillin",
            medical_history="None",
        )

    def test_list_patients_admin(self):
        """Test listing patients as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("patient-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_patients_patient_forbidden(self):
        """Test listing patients as patient (should be forbidden)"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse("patient-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_detail_owner(self):
        """Test getting patient details as the patient themselves"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse("patient-detail", kwargs={"id": self.patient.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blood_type"], "A+")
        self.assertEqual(response.data["allergies"], "Penicillin")

    def test_patient_detail_admin(self):
        """Test getting patient details as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("patient-detail", kwargs={"id": self.patient.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blood_type"], "A+")

    def test_patient_update_owner(self):
        """Test updating patient as the patient themselves"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse("patient-update", kwargs={"id": self.patient.id})
        data = {"blood_type": "B+", "allergies": "None", "medical_history": "Asthma"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.blood_type, "B+")
        self.assertEqual(self.patient.allergies, "None")
        self.assertEqual(self.patient.medical_history, "Asthma")

    def test_patient_update_admin(self):
        """Test updating patient as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("patient-update", kwargs={"id": self.patient.id})
        data = {"blood_type": "O-", "allergies": "Sulfa", "medical_history": "Diabetes"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.blood_type, "O-")
        self.assertEqual(self.patient.allergies, "Sulfa")
        self.assertEqual(self.patient.medical_history, "Diabetes")
