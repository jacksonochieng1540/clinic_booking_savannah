from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'license_number', 'is_available']
    list_filter = ['specialty', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specialty']