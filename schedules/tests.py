from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from doctors.models import Doctor
from .models import WorkingHours
from accounts.models import UserProfile

User = get_user_model()

class SchedulesTests(TestCase):
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
        
        # Create working hours
        self.working_hours = WorkingHours.objects.create(
            doctor=self.doctor,
            day_of_week='monday',
            start_time='09:00',
            end_time='17:00',
            is_available=True
        )

    def test_list_working_hours_doctor(self):
        """Test listing working hours as doctor"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('working-hours-list', kwargs={'doctor_id': self.doctor.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_working_hours_admin(self):
        """Test listing working hours as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('working-hours-list', kwargs={'doctor_id': self.doctor.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_working_hours_admin(self):
        """Test creating working hours as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('working-hours-create')
        data = {
            'doctor': self.doctor.id,
            'day_of_week': 'tuesday',
            'start_time': '09:00',
            'end_time': '17:00',
            'is_available': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkingHours.objects.count(), 2)

    def test_create_working_hours_doctor_forbidden(self):
        """Test creating working hours as doctor (should be forbidden)"""
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('working-hours-create')
        data = {
            'doctor': self.doctor.id,
            'day_of_week': 'tuesday',
            'start_time': '09:00',
            'end_time': '17:00',
            'is_available': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_working_hours_admin(self):
        """Test updating working hours as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('working-hours-update', kwargs={'id': self.working_hours.id})
        data = {
            'start_time': '10:00',
            'end_time': '18:00',
            'is_available': False
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.working_hours.refresh_from_db()
        self.assertEqual(str(self.working_hours.start_time), '10:00:00')
        self.assertEqual(str(self.working_hours.end_time), '18:00:00')
        self.assertFalse(self.working_hours.is_available)

    def test_doctor_availability(self):
        """Test getting doctor availability"""
        # Get a future Monday
        now = timezone.now()
        days_until_monday = (0 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        monday = now + timedelta(days=days_until_monday)
        date_str = monday.strftime('%Y-%m-%d')
        
        url = reverse('doctor-availability', kwargs={'doctor_id': self.doctor.id})
        response = self.client.get(url, {'date': date_str})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_slots', response.data)
        self.assertIn('total_slots', response.data)
        self.assertIn('available_count', response.data)

    def test_doctor_availability_invalid_date(self):
        """Test getting availability with invalid date"""
        url = reverse('doctor-availability', kwargs={'doctor_id': self.doctor.id})
        response = self.client.get(url, {'date': 'invalid-date'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_doctor_availability_past_date(self):
        """Test getting availability for past date"""
        past_date = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        url = reverse('doctor-availability', kwargs={'doctor_id': self.doctor.id})
        response = self.client.get(url, {'date': past_date})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)