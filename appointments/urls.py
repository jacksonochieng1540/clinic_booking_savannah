from django.urls import path
from . import views

urlpatterns = [
    path('', views.AppointmentListView.as_view(), name='appointment-list'),
    path('create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('<int:id>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<int:id>/cancel/', views.AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('<int:id>/reschedule/', views.AppointmentRescheduleView.as_view(), name='appointment-reschedule'),
    path('patients/<int:patient_id>/appointments/', 
         views.PatientAppointmentsView.as_view(), 
         name='patient-appointments'),
]