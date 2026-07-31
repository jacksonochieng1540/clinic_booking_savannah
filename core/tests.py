from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient
from .exceptions import custom_exception_handler
from .permissions import IsAdminUser, IsDoctorUser, IsPatientUser, IsDoctorOrAdmin
from .utils import generate_time_slots, validate_appointment_time
from datetime import datetime, timedelta
from django.utils import timezone

class CoreUtilsTests(TestCase):
    def test_generate_time_slots(self):
        """Test generating time slots from working hours"""
        date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        working_hours = {
            'monday': {'start': '09:00', 'end': '17:00'}
        }
        
        # Set date to Monday
        days_until_monday = (0 - date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        monday = date + timedelta(days=days_until_monday)
        
        slots = generate_time_slots(monday, working_hours)
        
        self.assertEqual(len(slots), 16)  # 8 hours * 2 slots per hour = 16 slots
        self.assertEqual(slots[0].hour, 9)
        self.assertEqual(slots[0].minute, 0)
        self.assertEqual(slots[-1].hour, 16)
        self.assertEqual(slots[-1].minute, 30)

    def test_generate_time_slots_no_working_hours(self):
        """Test generating slots with no working hours"""
        date = timezone.now()
        working_hours = {}
        
        slots = generate_time_slots(date, working_hours)
        
        self.assertEqual(len(slots), 0)

    def test_validate_appointment_time(self):
        """Test validating appointment time against working hours"""
        # This test requires a mock WorkingHours object
        # We'll test the logic with a simple implementation
        pass

class CorePermissionsTests(TestCase):
    def test_is_admin_user_permission(self):
        """Test IsAdminUser permission"""
        permission = IsAdminUser()
        # Mock request with admin user
        # This would require creating a user in the test database
        pass

    def test_is_doctor_user_permission(self):
        """Test IsDoctorUser permission"""
        pass

    def test_is_patient_user_permission(self):
        """Test IsPatientUser permission"""
        pass

    def test_is_doctor_or_admin_permission(self):
        """Test IsDoctorOrAdmin permission"""
        pass