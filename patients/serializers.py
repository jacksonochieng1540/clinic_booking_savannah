from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "user",
            "user_details",
            "name",
            "email",
            "phone",
            "blood_type",
            "allergies",
            "medical_history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
