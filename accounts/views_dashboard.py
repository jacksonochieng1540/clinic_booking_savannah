from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone

from appointments.models import Appointment
from doctors.models import Doctor
from patients.models import Patient

User = get_user_model()


@login_required
def dashboard_view(request):
    """
    Main dashboard - redirects based on user role
    """
    user = request.user

    if user.is_superuser or user.role == "admin":
        return redirect("admin_dashboard")
    elif user.role == "doctor":
        return redirect("doctor_dashboard")
    else:
        return redirect("patient_dashboard")


@login_required
def patient_dashboard(request):
    """
    Patient dashboard view
    """
    user = request.user

    try:
        patient = Patient.objects.get(user=user)
    except Patient.DoesNotExist:
        messages.warning(request, "Please complete your profile")
        return redirect("profile")

    now = timezone.now()

    upcoming_appointments = Appointment.objects.filter(
        patient=patient, start_time__gte=now, status__in=["scheduled", "confirmed"]
    ).order_by("start_time")[:10]

    past_appointments = Appointment.objects.filter(
        patient=patient, start_time__lt=now
    ).order_by("-start_time")[:10]

    total_appointments = Appointment.objects.filter(patient=patient).count()
    completed_appointments = Appointment.objects.filter(
        patient=patient, status="completed"
    ).count()
    cancelled_appointments = Appointment.objects.filter(
        patient=patient, status="cancelled"
    ).count()
    upcoming_count = Appointment.objects.filter(
        patient=patient, start_time__gte=now, status__in=["scheduled", "confirmed"]
    ).count()

    recent_doctors = Doctor.objects.filter(appointments__patient=patient).distinct()[:5]

    context = {
        "patient": patient,
        "upcoming_appointments": upcoming_appointments,
        "past_appointments": past_appointments,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "upcoming_count": upcoming_count,
        "recent_doctors": recent_doctors,
        "now": now,
    }

    return render(request, "dashboard/patient_dashboard.html", context)


@login_required
def doctor_dashboard(request):
    """
    Doctor dashboard view
    """
    user = request.user

    try:
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        messages.warning(request, "Please complete your profile")
        return redirect("profile")

    now = timezone.now()

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        start_time__gte=today_start,
        start_time__lt=today_end,
        status__in=["scheduled", "confirmed"],
    ).order_by("start_time")

    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor, start_time__gte=now, status__in=["scheduled", "confirmed"]
    ).order_by("start_time")[:20]

    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    today_count = today_appointments.count()
    upcoming_count = Appointment.objects.filter(
        doctor=doctor, start_time__gte=now, status__in=["scheduled", "confirmed"]
    ).count()

    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=7)

    weekly_appointments = Appointment.objects.filter(
        doctor=doctor, start_time__gte=week_start, start_time__lt=week_end
    )

    context = {
        "doctor": doctor,
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "total_appointments": total_appointments,
        "today_count": today_count,
        "upcoming_count": upcoming_count,
        "weekly_appointments": weekly_appointments,
        "now": now,
    }

    return render(request, "dashboard/doctor_dashboard.html", context)


@login_required
def admin_dashboard(request):
    """
    Admin dashboard view
    """
    if not (request.user.is_superuser or request.user.role == "admin"):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("home")

    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_appointments = Appointment.objects.filter(
        start_time__gte=today_start, start_time__lt=today_end
    ).count()

    upcoming_appointments = Appointment.objects.filter(
        start_time__gte=now, status__in=["scheduled", "confirmed"]
    ).count()

    completed_appointments = Appointment.objects.filter(status="completed").count()
    cancelled_appointments = Appointment.objects.filter(status="cancelled").count()

    recent_appointments = Appointment.objects.all().order_by("-created_at")[:10]
    recent_users = User.objects.all().order_by("-date_joined")[:10]

    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_appointments = Appointment.objects.filter(
        created_at__gte=month_start
    ).count()

    context = {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "recent_appointments": recent_appointments,
        "recent_users": recent_users,
        "monthly_appointments": monthly_appointments,
    }

    return render(request, "dashboard/admin_dashboard.html", context)
