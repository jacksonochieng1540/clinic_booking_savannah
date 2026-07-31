from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Doctor
from accounts.models import UserProfile

User = get_user_model()

class DoctorsTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_superuser=True,
            is_staff=True
        )
        UserProfile.objects.create(user=self.admin_user)
        
        # Create doctor user
        self.doctor_user = User.objects.create_user(
            email='doctor@example.com',
            username='doctoruser',
            password='DoctorPass123!',
            first_name='John',
            last_name='Smith',
            role='doctor'
        )
        UserProfile.objects.create(user=self.doctor_user)
        
        # Create doctor profile
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty='Cardiology',
            license_number='LIC12345',
            years_of_experience=5,
            consultation_fee=150.00,
            is_available=True
        )
        
        # Create patient user
        self.patient_user = User.objects.create_user(
            email='patient@example.com',
            username='patientuser',
            password='PatientPass123!',
            first_name='Patient',
            last_name='User',
            role='patient'
        )
        UserProfile.objects.create(user=self.patient_user)

    def test_list_doctors_success(self):
        """Test listing all doctors"""
        url = reverse('doctor-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        
    def test_doctor_detail_success(self):
        """Test getting doctor details"""
        url = reverse('doctor-detail', kwargs={'id': self.doctor.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialty'], 'Cardiology')
        self.assertEqual(response.data['license_number'], 'LIC12345')

    def test_doctor_create_admin(self):
        """Test creating doctor as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctor-create')
        data = {
            'user': self.admin_user.id,
            'specialty': 'Neurology',
            'license_number': 'LIC67890',
            'years_of_experience': 10,
            'consultation_fee': 200.00,
            'is_available': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doctor.objects.count(), 2)

    def test_doctor_create_patient_forbidden(self):
        """Test creating doctor as patient (should be forbidden)"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctor-create')
        data = {
            'user': self.patient_user.id,
            'specialty': 'Neurology',
            'license_number': 'LIC67890',
            'years_of_experience': 10,
            'consultation_fee': 200.00,
            'is_available': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_update_doctor(self):
        """Test updating doctor as the doctor themselves"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('doctor-update', kwargs={'id': self.doctor.id})
        data = {
            'specialty': 'Cardiology',
            'license_number': 'LIC12345',
            'years_of_experience': 6,
            'consultation_fee': 175.00,
            'is_available': False
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.years_of_experience, 6)
        self.assertEqual(self.doctor.consultation_fee, 175.00)
        self.assertFalse(self.doctor.is_available)

    def test_doctor_update_admin(self):
        """Test updating doctor as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('doctor-update', kwargs={'id': self.doctor.id})
        data = {
            'specialty': 'Cardiology',
            'license_number': 'LIC12345',
            'years_of_experience': 7,
            'consultation_fee': 200.00,
            'is_available': True
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.years_of_experience, 7)
        self.assertEqual(self.doctor.consultation_fee, 200.00)

    def test_doctor_update_patient_forbidden(self):
        """Test updating doctor as patient (should be forbidden)"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('doctor-update', kwargs={'id': self.doctor.id})
        data = {
            'specialty': 'Cardiology',
            'license_number': 'LIC12345',
            'years_of_experience': 8,
            'consultation_fee': 300.00,
            'is_available': True
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)