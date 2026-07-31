from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "user",
            "user_details",
            "name",
            "email",
            "phone",
            "specialty",
            "license_number",
            "years_of_experience",
            "bio",
            "consultation_fee",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class DoctorListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Doctor
        fields = ["id", "name", "specialty", "consultation_fee", "is_available"]
