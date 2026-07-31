from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
import pytz

from doctors.models import Doctor
from .models import WorkingHours
from .serializers import WorkingHoursSerializer, WorkingHoursListSerializer
from core.utils import generate_time_slots
from appointments.models import Appointment
from core.permissions import IsDoctorOrAdmin, IsAdminUser

class WorkingHoursListView(generics.ListAPIView):
    """List all working hours for a doctor"""
    permission_classes = [IsDoctorOrAdmin]
    serializer_class = WorkingHoursListSerializer
    
    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        doctor = get_object_or_404(Doctor, id=doctor_id)
        return WorkingHours.objects.filter(
            doctor=doctor,
            is_available=True
        )

class WorkingHoursCreateView(generics.CreateAPIView):
    """Create working hours for a doctor"""
    permission_classes = [IsAdminUser]
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer

class WorkingHoursUpdateView(generics.UpdateAPIView):
    """Update working hours"""
    permission_classes = [IsAdminUser]
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer
    lookup_field = 'id'

class DoctorAvailabilityView(generics.GenericAPIView):
    """Get available slots for a doctor on a given date"""
    permission_classes = []
    
    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'error': 'Date parameter is required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            date = pytz.UTC.localize(date)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if date.date() < timezone.now().date():
            return Response(
                {'error': 'Cannot view availability for past dates'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        working_hours = WorkingHours.objects.filter(
            doctor=doctor,
            day_of_week=date.strftime('%A').lower(),
            is_available=True
        )
        
        if not working_hours.exists():
            return Response({
                'doctor_id': doctor.id,
                'doctor_name': doctor.name,
                'date': date_str,
                'available_slots': [],
                'message': 'Doctor is not available on this day'
            })
        
        all_slots = []
        for wh in working_hours:
            wh_data = {
                wh.day_of_week: {
                    'start': wh.start_time.strftime('%H:%M'),
                    'end': wh.end_time.strftime('%H:%M')
                }
            }
            slots = generate_time_slots(date, wh_data)
            all_slots.extend(slots)
        
        booked_slots = Appointment.objects.filter(
            doctor=doctor,
            start_time__date=date.date(),
            status__in=['scheduled', 'confirmed']
        ).values_list('start_time', flat=True)
        
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        slots_data = [
            {
                'start_time': slot.isoformat(),
                'end_time': (slot + timezone.timedelta(minutes=30)).isoformat()
            }
            for slot in available_slots
        ]
        
        return Response({
            'doctor_id': doctor.id,
            'doctor_name': doctor.name,
            'date': date_str,
            'available_slots': slots_data,
            'total_slots': len(all_slots),
            'booked_slots': len(booked_slots),
            'available_count': len(available_slots)
        })