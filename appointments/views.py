from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.email import (
    send_appointment_cancellation_email,
    send_appointment_confirmation_email,
    send_appointment_reschedule_email,
)
from core.permissions import IsAdminUser, IsDoctorUser, IsPatientUser
from doctors.models import Doctor

from .models import Appointment
from .serializers import (
    AppointmentCancelSerializer,
    AppointmentCreateSerializer,
    AppointmentListSerializer,
    AppointmentRescheduleSerializer,
    AppointmentSerializer,
)


def _error_message(exc):
    """Flatten an exception raised by appointment business rules to a string"""
    if isinstance(exc, DjangoValidationError):
        return "; ".join(exc.messages)
    return str(exc)


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

        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class AppointmentCancelView(generics.GenericAPIView):
    """Cancel an appointment"""

    permission_classes = [IsPatientUser]
    serializer_class = AppointmentCancelSerializer

    def patch(self, request, id):
        appointment = get_object_or_404(Appointment, id=id)

        if appointment.status == "cancelled":
            return Response(
                {"error": "Appointment is already cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            appointment.cancel(reason=serializer.validated_data.get("reason"))
        except (ValueError, DjangoValidationError) as exc:
            return Response({"error": _error_message(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Send cancellation email
        send_appointment_cancellation_email(appointment)

        return Response(
            {
                "message": "Appointment cancelled successfully",
                "appointment": AppointmentSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )


class AppointmentRescheduleView(generics.GenericAPIView):
    """Reschedule an appointment"""

    permission_classes = [IsPatientUser]
    serializer_class = AppointmentRescheduleSerializer

    def patch(self, request, id):
        appointment = get_object_or_404(Appointment, id=id)

        if appointment.status == "cancelled":
            return Response(
                {"error": "Cannot reschedule a cancelled appointment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_start_time = serializer.validated_data["new_start_time"]
        try:
            old_time = appointment.reschedule(new_start_time)
        except (ValueError, DjangoValidationError) as exc:
            return Response({"error": _error_message(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Send reschedule email
        send_appointment_reschedule_email(appointment, old_time)

        return Response(
            {
                "message": "Appointment rescheduled successfully",
                "appointment": AppointmentSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )


class PatientAppointmentsView(generics.GenericAPIView):
    """Get upcoming appointments for a patient (Bonus)"""

    permission_classes = [IsPatientUser]

    def get(self, request, patient_id):
        from patients.models import Patient

        patient = get_object_or_404(Patient, id=patient_id)

        upcoming = patient.appointments.filter(status__in=["scheduled", "confirmed"], start_time__gte=timezone.now()).order_by(
            "start_time"
        )

        serializer = AppointmentListSerializer(upcoming, many=True)

        return Response(
            {
                "patient_id": patient.id,
                "patient_name": patient.name,
                "upcoming_appointments": serializer.data,
                "count": upcoming.count(),
            }
        )


class AppointmentDetailView(generics.RetrieveAPIView):
    """Get appointment details"""

    permission_classes = [IsPatientUser | IsDoctorUser | IsAdminUser]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = "id"


class AppointmentListView(generics.ListAPIView):
    """List appointments with filters"""

    permission_classes = [IsPatientUser | IsDoctorUser | IsAdminUser]
    serializer_class = AppointmentListSerializer

    def get_queryset(self):
        queryset = Appointment.objects.all()
        doctor_id = self.request.query_params.get("doctor_id")
        patient_id = self.request.query_params.get("patient_id")
        status_filter = self.request.query_params.get("status")

        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-start_time")


@login_required
def book_appointment_view(request):
    """Book appointment page"""
    doctors = Doctor.objects.filter(is_available=True)
    return render(request, "appointments/book.html", {"doctors": doctors})


@login_required
def appointment_list_view(request):
    """List all appointments for the logged-in user"""
    user = request.user
    appointments = Appointment.objects.filter(patient__user=user).order_by("-start_time")

    return render(
        request,
        "appointments/list.html",
        {
            "appointments": appointments,
            "upcoming_count": appointments.filter(
                start_time__gte=timezone.now(), status__in=["scheduled", "confirmed"]
            ).count(),
            "past_count": appointments.filter(start_time__lt=timezone.now()).count(),
        },
    )


@login_required
def appointment_detail_view(request, id):
    """Appointment detail page"""
    appointment = get_object_or_404(Appointment, id=id)

    # Check if user has access
    if request.user.role == "patient" and appointment.patient.user != request.user:
        messages.error(request, "You don't have permission to view this appointment.")
        return redirect("appointment_list")

    return render(request, "appointments/detail.html", {"appointment": appointment})


@login_required
def cancel_appointment_view(request, id):
    """Cancel appointment from frontend"""
    appointment = get_object_or_404(Appointment, id=id)

    if request.method == "POST":
        reason = request.POST.get("reason", "Cancelled by patient")
        try:
            appointment.cancel(reason=reason)
            messages.success(request, "Appointment cancelled successfully.")
            send_appointment_cancellation_email(appointment)
        except Exception as e:
            messages.error(request, str(e))
        return redirect("appointment_detail", id=id)

    return render(request, "appointments/cancel.html", {"appointment": appointment})


@login_required
def reschedule_appointment_view(request, id):
    """Reschedule appointment from frontend"""
    appointment = get_object_or_404(Appointment, id=id)

    if request.method == "POST":
        new_start_time_str = request.POST.get("new_start_time")
        if not new_start_time_str:
            messages.error(request, "Please select a new time.")
            return render(request, "appointments/reschedule.html", {"appointment": appointment})

        try:
            new_start_time = timezone.datetime.fromisoformat(new_start_time_str)
            old_time = appointment.reschedule(new_start_time)
            send_appointment_reschedule_email(appointment, old_time)
            messages.success(request, "Appointment rescheduled successfully.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect("appointment_detail", id=id)

    return render(request, "appointments/reschedule.html", {"appointment": appointment})
