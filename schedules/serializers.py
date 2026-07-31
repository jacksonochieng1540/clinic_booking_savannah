from rest_framework import serializers

from .models import WorkingHours


class WorkingHoursSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = WorkingHours
        fields = [
            "id",
            "doctor",
            "doctor_name",
            "day_of_week",
            "start_time",
            "end_time",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class WorkingHoursListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ["day_of_week", "start_time", "end_time", "is_available"]
