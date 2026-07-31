from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from doctors.models import Doctor
from patients.models import Patient
from schedules.models import WorkingHours
from .models import Appointment
from accounts.models import UserProfile

User = get_user_model()

class AppointmentsTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all tests"""
        # Create patient user
        cls.patient_user = User.objects.create_user(
            email='patient@example.com',
            username='patientuser',
            password='PatientPass123!',
            first_name='Jane',
            last_name='Doe',
            role='patient'
        )
        UserProfile.objects.create(user=cls.patient_user)
        cls.patient = Patient.objects.create(
            user=cls.patient_user,
            blood_type='A+',
            allergies='None',
            medical_history='None'
        )
        
        # Create doctor user
        cls.doctor_user = User.objects.create_user(
            email='doctor@example.com',
            username='doctoruser',
            password='DoctorPass123!',
            first_name='John',
            last_name='Smith',
            role='doctor'
        )
        UserProfile.objects.create(user=cls.doctor_user)
        cls.doctor = Doctor.objects.create(
            user=cls.doctor_user,
            specialty='Cardiology',
            license_number='LIC12345',
            years_of_experience=5,
            consultation_fee=150.00,
            is_available=True
        )
        
        # Create working hours for ALL days with proper times
        all_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in all_days:
            WorkingHours.objects.create(
                doctor=cls.doctor,
                day_of_week=day,
                start_time='09:00:00',
                end_time='17:00:00',
                is_available=True
            )
    
    def setUp(self):
        """Set up test client and dates for each test"""
        self.client = APIClient()
        
        # Get a future date that's at least 3 days ahead
        now = timezone.now()
        self.future_date = now + timedelta(days=3)
        # Set to 10:00 AM
        self.future_date = self.future_date.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Past date - 3 days ago
        self.past_date = now - timedelta(days=3)
        self.past_date = self.past_date.replace(hour=10, minute=0, second=0, microsecond=0)

    def test_create_appointment_success(self):
        """Test successful appointment creation"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-create')
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'First appointment'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(response.data['patient_name'], 'Jane Doe')
        self.assertEqual(response.data['doctor_name'], 'Dr. John Smith')
        self.assertEqual(response.data['status'], 'scheduled')

    def test_create_appointment_double_booking(self):
        """Test preventing double-booking"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-create')
        
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'First appointment'
        }
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already booked', str(response2.data))

    def test_create_appointment_outside_working_hours(self):
        """Test creating appointment outside working hours"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-create')
        
        # Try to book at 6:00 AM (before working hours of 9:00 AM)
        early_time = self.future_date.replace(hour=6, minute=0)
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': early_time.isoformat(),
            'notes': 'Early appointment'
        }
        response = self.client.post(url, data, format='json')
        
        # Should fail with validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The model's clean() method will raise this error
        self.assertIn('working hours', str(response.data).lower())

    def test_create_appointment_past_date(self):
        """Test creating appointment in the past"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-create')
        
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.past_date.isoformat(),
            'notes': 'Past appointment'
        }
        response = self.client.post(url, data, format='json')
        
        # Should fail because date is in the past
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The model's clean() method will raise this error
        self.assertIn('past', str(response.data).lower())

    def test_create_appointment_within_1_hour_bonus(self):
        """Test preventing bookings within 1 hour (Bonus)"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-create')
        
        # Create a time that is 30 minutes from now
        within_hour = timezone.now() + timedelta(minutes=30)
        # Make sure it's on a 30-minute boundary
        if within_hour.minute not in [0, 30]:
            within_hour = within_hour.replace(minute=0 if within_hour.minute < 30 else 30, second=0, microsecond=0)
        
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': within_hour.isoformat(),
            'notes': 'Within 1 hour'
        }
        response = self.client.post(url, data, format='json')
        
        # Should fail with 1 hour error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The model's clean() method will raise this error
        self.assertIn('1 hour', str(response.data).lower())

    def test_create_appointment_30_minute_boundary(self):
        """Test that appointments must start at :00 or :30"""
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-create')
        
        invalid_time = self.future_date.replace(hour=10, minute=15)
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': invalid_time.isoformat(),
            'notes': 'Invalid time'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(':00 or :30', str(response.data))

    def test_cancel_appointment_success(self):
        """Test successful appointment cancellation"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'Test appointment'
        }
        create_response = self.client.post(create_url, data, format='json')
        appointment_id = create_response.data['id']
        
        cancel_url = reverse('appointment-cancel', kwargs={'id': appointment_id})
        cancel_data = {'reason': 'Patient is sick'}
        response = self.client.patch(cancel_url, cancel_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Appointment cancelled successfully')
        self.assertEqual(response.data['appointment']['status'], 'cancelled')
        self.assertEqual(response.data['appointment']['cancellation_reason'], 'Patient is sick')

    def test_cancel_already_cancelled(self):
        """Test cancelling an already cancelled appointment"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'Test appointment'
        }
        create_response = self.client.post(create_url, data, format='json')
        appointment_id = create_response.data['id']
        
        cancel_url = reverse('appointment-cancel', kwargs={'id': appointment_id})
        self.client.patch(cancel_url, {'reason': 'Test'}, format='json')
        
        response = self.client.patch(cancel_url, {'reason': 'Again'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already cancelled', str(response.data))

    def test_reschedule_appointment_success(self):
        """Test successful appointment rescheduling"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'Test appointment'
        }
        create_response = self.client.post(create_url, data, format='json')
        appointment_id = create_response.data['id']
        
        # Reschedule to 2:00 PM on same day
        new_time = self.future_date.replace(hour=14, minute=0)
        reschedule_url = reverse('appointment-reschedule', kwargs={'id': appointment_id})
        reschedule_data = {'new_start_time': new_time.isoformat()}
        response = self.client.patch(reschedule_url, reschedule_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Appointment rescheduled successfully')
        
        # Verify the new time
        appointment_obj = Appointment.objects.get(id=appointment_id)
        self.assertEqual(appointment_obj.start_time.hour, 14)
        self.assertEqual(appointment_obj.start_time.minute, 0)

    def test_reschedule_to_booked_slot(self):
        """Test rescheduling to an already booked slot"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        
        # Create first appointment at 10:00 AM
        data1 = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'First appointment'
        }
        response1 = self.client.post(create_url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Create second appointment at 11:00 AM
        second_time = self.future_date.replace(hour=11, minute=0)
        data2 = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': second_time.isoformat(),
            'notes': 'Second appointment'
        }
        response2 = self.client.post(create_url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        appointment2_id = response2.data['id']
        
        # Try to reschedule second appointment to the first appointment's time
        reschedule_url = reverse('appointment-reschedule', kwargs={'id': appointment2_id})
        reschedule_data = {'new_start_time': self.future_date.isoformat()}
        response = self.client.patch(reschedule_url, reschedule_data, format='json')
        
        # Should fail because the slot is already booked
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already booked', str(response.data))

    def test_reschedule_cancelled_appointment(self):
        """Test rescheduling a cancelled appointment"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'Test appointment'
        }
        create_response = self.client.post(create_url, data, format='json')
        appointment_id = create_response.data['id']
        
        # Cancel appointment
        cancel_url = reverse('appointment-cancel', kwargs={'id': appointment_id})
        self.client.patch(cancel_url, {'reason': 'Test'}, format='json')
        
        # Try to reschedule
        reschedule_url = reverse('appointment-reschedule', kwargs={'id': appointment_id})
        new_time = self.future_date.replace(hour=14, minute=0)
        reschedule_data = {'new_start_time': new_time.isoformat()}
        response = self.client.patch(reschedule_url, reschedule_data, format='json')
        
        # Should fail because appointment is cancelled
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cancelled', str(response.data))

    def test_patient_appointments_bonus(self):
        """Test getting patient's upcoming appointments (Bonus)"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        
        # Create two appointments
        time1 = self.future_date.replace(hour=10, minute=0)
        data1 = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': time1.isoformat(),
            'notes': 'First appointment'
        }
        self.client.post(create_url, data1, format='json')
        
        time2 = self.future_date.replace(hour=11, minute=0)
        data2 = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': time2.isoformat(),
            'notes': 'Second appointment'
        }
        self.client.post(create_url, data2, format='json')
        
        # Get patient's appointments
        url = reverse('patient-appointments', kwargs={'patient_id': self.patient.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_id'], self.patient.id)
        self.assertEqual(response.data['patient_name'], 'Jane Doe')
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['upcoming_appointments']), 2)

    def test_list_appointments_with_filters(self):
        """Test listing appointments with filters"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'Test appointment'
        }
        self.client.post(create_url, data, format='json')
        
        url = reverse('appointment-list')
        response = self.client.get(url, {'doctor_id': self.doctor.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_appointment_detail(self):
        """Test getting appointment details"""
        self.client.force_authenticate(user=self.patient_user)
        
        create_url = reverse('appointment-create')
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'start_time': self.future_date.isoformat(),
            'notes': 'Test appointment'
        }
        create_response = self.client.post(create_url, data, format='json')
        appointment_id = create_response.data['id']
        
        url = reverse('appointment-detail', kwargs={'id': appointment_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], appointment_id)
        self.assertEqual(response.data['patient_name'], 'Jane Doe')
        self.assertEqual(response.data['doctor_name'], 'Dr. John Smith')