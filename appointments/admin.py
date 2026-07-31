from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'start_time', 'status']
    list_filter = ['status', 'doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name']
    date_hierarchy = 'start_time'