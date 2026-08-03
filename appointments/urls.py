from django.urls import path

from . import views

urlpatterns = [
    path("", views.appointment_list_view, name="appointment_list"),
    path("book/", views.book_appointment_view, name="book_appointment"),
    path("<int:id>/", views.appointment_detail_view, name="appointment_detail"),
    path("<int:id>/cancel/", views.cancel_appointment_view, name="cancel_appointment"),
    path("<int:id>/reschedule/", views.reschedule_appointment_view, name="reschedule_appointment"),
    path("api/", views.AppointmentListView.as_view(), name="appointment-list"),
    path("api/create/", views.AppointmentCreateView.as_view(), name="appointment-create"),
    path(
        "api/<int:id>/",
        views.AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
    path(
        "api/<int:id>/cancel/",
        views.AppointmentCancelView.as_view(),
        name="appointment-cancel",
    ),
    path(
        "api/<int:id>/reschedule/",
        views.AppointmentRescheduleView.as_view(),
        name="appointment-reschedule",
    ),
    path(
        "api/patients/<int:patient_id>/appointments/",
        views.PatientAppointmentsView.as_view(),
        name="patient-appointments",
    ),
]
