from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from .models import Appointment
from doctors.serializers import DoctorListSerializer
from patients.serializers import PatientSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.SerializerMethodField()  # ← Change this
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorListSerializer(source='doctor', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'patient_details',
            'doctor', 'doctor_name', 'doctor_details',
            'start_time', 'end_time', 'status', 
            'cancellation_reason', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'cancellation_reason', 'created_at', 'updated_at']
    
    def get_doctor_name(self, obj):
        """Return doctor name with Dr. prefix"""
        return f"Dr. {obj.doctor.user.get_full_name()}"

class AppointmentCreateSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    doctor_id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_start_time(self, value):
        if value.minute not in [0, 30]:
            raise serializers.ValidationError(
                "Appointments must start at :00 or :30"
            )
        return value
    
    def validate(self, data):
        from patients.models import Patient
        from doctors.models import Doctor
        
        patient_id = data.get('patient_id')
        doctor_id = data.get('doctor_id')
        start_time = data.get('start_time')
        
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            raise serializers.ValidationError({
                'patient_id': 'Patient not found'
            })
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError({
                'doctor_id': 'Doctor not found'
            })
        
        end_time = start_time + timezone.timedelta(minutes=30)
        
        if Appointment.objects.filter(
            doctor=doctor,
            start_time=start_time,
            status__in=['scheduled', 'confirmed']
        ).exists():
            raise serializers.ValidationError(
                'This time slot is already booked'
            )
        
        data['patient'] = patient
        data['doctor'] = doctor
        data['end_time'] = end_time
        
        return data
    
    def create(self, validated_data):
        try:
            return Appointment.objects.create(
                patient=validated_data['patient'],
                doctor=validated_data['doctor'],
                start_time=validated_data['start_time'],
                end_time=validated_data['end_time'],
                notes=validated_data.get('notes', '')
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)

class AppointmentCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)

class AppointmentRescheduleSerializer(serializers.Serializer):
    new_start_time = serializers.DateTimeField()
    
    def validate_new_start_time(self, value):
        if value.minute not in [0, 30]:
            raise serializers.ValidationError(
                "Appointments must start at :00 or :30"
            )
        return value

class AppointmentListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient_name', 'doctor_name', 'start_time', 'status']