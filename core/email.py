from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email(subject, to_email, template_name, context, from_email=None):
    """
    Send email using HTML template
    """
    try:
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_welcome_email(user):
    context = {
        'user': user,
        'full_name': user.get_full_name(),
        'login_url': 'https://yourdomain.com/login/',
        'support_email': settings.DEFAULT_FROM_EMAIL,
    }
    return send_email(
        subject='Welcome to Clinic Booking System',
        to_email=user.email,
        template_name='emails/welcome.html',
        context=context
    )

def send_appointment_confirmation_email(appointment):
    context = {
        'appointment': appointment,
        'patient_name': appointment.patient.user.get_full_name(),
        'doctor_name': appointment.doctor.user.get_full_name(),
        'date': appointment.start_time.strftime('%B %d, %Y'),
        'time': appointment.start_time.strftime('%I:%M %p'),
        'cancel_url': f'https://yourdomain.com/appointments/{appointment.id}/cancel/',
    }
    return send_email(
        subject=f'Appointment Confirmation - {appointment.start_time.strftime("%B %d")}',
        to_email=appointment.patient.user.email,
        template_name='emails/appointment_confirmation.html',
        context=context
    )

def send_appointment_cancellation_email(appointment):
    context = {
        'appointment': appointment,
        'patient_name': appointment.patient.user.get_full_name(),
        'doctor_name': appointment.doctor.user.get_full_name(),
        'date': appointment.start_time.strftime('%B %d, %Y'),
        'time': appointment.start_time.strftime('%I:%M %p'),
        'reason': appointment.cancellation_reason or 'Not specified',
    }
    return send_email(
        subject='Appointment Cancellation Confirmation',
        to_email=appointment.patient.user.email,
        template_name='emails/appointment_cancellation.html',
        context=context
    )

def send_appointment_reschedule_email(appointment, old_time):
    context = {
        'appointment': appointment,
        'patient_name': appointment.patient.user.get_full_name(),
        'doctor_name': appointment.doctor.user.get_full_name(),
        'new_date': appointment.start_time.strftime('%B %d, %Y'),
        'new_time': appointment.start_time.strftime('%I:%M %p'),
        'old_date': old_time.strftime('%B %d, %Y'),
        'old_time': old_time.strftime('%I:%M %p'),
    }
    return send_email(
        subject=f'Appointment Rescheduled - {appointment.start_time.strftime("%B %d")}',
        to_email=appointment.patient.user.email,
        template_name='emails/appointment_reschedule.html',
        context=context
    )

def send_password_reset_email(user, reset_link):
    context = {
        'user': user,
        'full_name': user.get_full_name(),
        'reset_link': reset_link,
        'support_email': settings.DEFAULT_FROM_EMAIL,
    }
    return send_email(
        subject='Password Reset Request',
        to_email=user.email,
        template_name='emails/password_reset.html',
        context=context
    )