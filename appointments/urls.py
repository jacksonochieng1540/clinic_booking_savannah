from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.AppointmentListView.as_view(), name='appointment-list'),
    path('api/create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('api/<int:id>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('api/<int:id>/cancel/', views.AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('api/<int:id>/reschedule/', views.AppointmentRescheduleView.as_view(), name='appointment-reschedule'),
    path('api/patients/<int:patient_id>/appointments/', 
         views.PatientAppointmentsView.as_view(), 
         name='patient-appointments'),
]