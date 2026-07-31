from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from doctors.models import Doctor
from patients.models import Patient
from schedules.models import WorkingHours

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        related_name='appointments'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='scheduled'
    )
    cancellation_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['doctor', 'start_time', 'status']),
            models.Index(fields=['patient', 'start_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name} - {self.start_time}"

    def clean(self):
        duration = (self.end_time - self.start_time).total_seconds()
        if duration != 1800:
            raise ValidationError('Appointment must be 30 minutes long')
        
        if self.start_time < timezone.now():
            raise ValidationError('Cannot book in the past')
        
        day_name = self.start_time.strftime('%A').lower()
        working_hours = WorkingHours.objects.filter(
            doctor=self.doctor,
            day_of_week=day_name,
            is_available=True
        )
        
        if not working_hours.exists():
            raise ValidationError('Doctor is not available on this day')
        
        is_valid = False
        for wh in working_hours:
            work_start = timezone.make_aware(
                timezone.datetime.combine(
                    self.start_time.date(),
                    wh.start_time
                )
            )
            work_end = timezone.make_aware(
                timezone.datetime.combine(
                    self.start_time.date(),
                    wh.end_time
                )
            )
            if work_start <= self.start_time < self.end_time <= work_end:
                is_valid = True
                break
        
        if not is_valid:
            raise ValidationError('Outside doctor\'s working hours')
        
        conflict_check = Appointment.objects.filter(
            doctor=self.doctor,
            start_time=self.start_time,
            status__in=['scheduled', 'confirmed']
        )
        if self.pk:
            conflict_check = conflict_check.exclude(pk=self.pk)
        
        if conflict_check.exists():
            raise ValidationError('This time slot is already booked')
        
        if self.start_time < timezone.now() + timezone.timedelta(hours=1):
            raise ValidationError(
                'Bookings must be made at least 1 hour in advance'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def cancel(self, reason=None):
        if self.status == 'cancelled':
            raise ValueError('Appointment is already cancelled')
        
        self.status = 'cancelled'
        self.cancellation_reason = reason
        self.save()
        return self

    def reschedule(self, new_start_time):
        if self.status == 'cancelled':
            raise ValueError('Cannot reschedule a cancelled appointment')
        
        new_end_time = new_start_time + timezone.timedelta(minutes=30)
        
        if new_start_time < timezone.now():
            raise ValueError('Cannot reschedule to a time in the past')
        
        if new_start_time < timezone.now() + timezone.timedelta(hours=1):
            raise ValueError(
                'Rescheduling must be at least 1 hour in advance'
            )
        
        day_name = new_start_time.strftime('%A').lower()
        working_hours = WorkingHours.objects.filter(
            doctor=self.doctor,
            day_of_week=day_name,
            is_available=True
        )
        
        if not working_hours.exists():
            raise ValueError('Doctor is not available on this day')
        
        is_valid = False
        for wh in working_hours:
            work_start = timezone.make_aware(
                timezone.datetime.combine(
                    new_start_time.date(),
                    wh.start_time
                )
            )
            work_end = timezone.make_aware(
                timezone.datetime.combine(
                    new_start_time.date(),
                    wh.end_time
                )
            )
            if work_start <= new_start_time < new_end_time <= work_end:
                is_valid = True
                break
        
        if not is_valid:
            raise ValueError('The new time is outside doctor\'s working hours')
        
        if Appointment.objects.filter(
            doctor=self.doctor,
            start_time=new_start_time,
            status__in=['scheduled', 'confirmed']
        ).exclude(pk=self.pk).exists():
            raise ValueError('The new time slot is already booked')
        
        old_time = self.start_time
        self.start_time = new_start_time
        self.end_time = new_end_time
        self.save()
        return old_time