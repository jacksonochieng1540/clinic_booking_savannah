from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError  


from .models import Appointment
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer,
    AppointmentCancelSerializer, AppointmentRescheduleSerializer,
    AppointmentListSerializer
)
from core.permissions import IsPatientUser, IsDoctorUser, IsAdminUser
from core.email import (
    send_appointment_confirmation_email,
    send_appointment_cancellation_email,
    send_appointment_reschedule_email
)

class AppointmentCreateView(generics.CreateAPIView):
    """Create a new appointment"""
    permission_classes = [IsPatientUser]
    serializer_class = AppointmentCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        
        # Send confirmation email
        send_appointment_confirmation_email(appointment)
        
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_201_CREATED
        )

class AppointmentCancelView(generics.GenericAPIView):
    """Cancel an appointment"""
    permission_classes = [IsPatientUser]
    serializer_class = AppointmentCancelSerializer
    
    def patch(self, request, id):
        appointment = get_object_or_404(Appointment, id=id)
        
        if appointment.status == 'cancelled':
            return Response(
                {'error': 'Appointment is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        appointment.cancel(reason=serializer.validated_data.get('reason'))
        
        # Send cancellation email
        send_appointment_cancellation_email(appointment)
        
        return Response(
            {
                'message': 'Appointment cancelled successfully',
                'appointment': AppointmentSerializer(appointment).data
            },
            status=status.HTTP_200_OK
        )

class AppointmentRescheduleView(generics.GenericAPIView):
    """Reschedule an appointment"""
    permission_classes = [IsPatientUser]
    serializer_class = AppointmentRescheduleSerializer
    
    def patch(self, request, id):
        appointment = get_object_or_404(Appointment, id=id)
        
        if appointment.status == 'cancelled':
            return Response(
                {'error': 'Cannot reschedule a cancelled appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_start_time = serializer.validated_data['new_start_time']
        old_time = appointment.reschedule(new_start_time)
        
        # Send reschedule email
        send_appointment_reschedule_email(appointment, old_time)
        
        return Response(
            {
                'message': 'Appointment rescheduled successfully',
                'appointment': AppointmentSerializer(appointment).data
            },
            status=status.HTTP_200_OK
        )

class PatientAppointmentsView(generics.GenericAPIView):
    """Get upcoming appointments for a patient (Bonus)"""
    permission_classes = [IsPatientUser]
    
    def get(self, request, patient_id):
        from patients.models import Patient
        patient = get_object_or_404(Patient, id=patient_id)
        
        upcoming = patient.appointments.filter(
            status__in=['scheduled', 'confirmed'],
            start_time__gte=timezone.now()
        ).order_by('start_time')
        
        serializer = AppointmentListSerializer(upcoming, many=True)
        
        return Response({
            'patient_id': patient.id,
            'patient_name': patient.name,
            'upcoming_appointments': serializer.data,
            'count': upcoming.count()
        })

class AppointmentDetailView(generics.RetrieveAPIView):
    """Get appointment details"""
    permission_classes = [IsPatientUser | IsDoctorUser | IsAdminUser]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = 'id'

class AppointmentListView(generics.ListAPIView):
    """List appointments with filters"""
    permission_classes = [IsPatientUser | IsDoctorUser | IsAdminUser]
    serializer_class = AppointmentListSerializer
    
    def get_queryset(self):
        queryset = Appointment.objects.all()
        doctor_id = self.request.query_params.get('doctor_id')
        patient_id = self.request.query_params.get('patient_id')
        status_filter = self.request.query_params.get('status')
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-start_time')