from django.urls import path
from . import views

urlpatterns = [
    path('api/doctors/<int:doctor_id>/working-hours/', 
         views.WorkingHoursListView.as_view(), 
         name='working-hours-list'),
    path('api/working-hours/create/', 
         views.WorkingHoursCreateView.as_view(), 
         name='working-hours-create'),
    path('api/working-hours/<int:id>/update/', 
         views.WorkingHoursUpdateView.as_view(), 
         name='working-hours-update'),
    path('api/doctors/<int:doctor_id>/availability/', 
         views.DoctorAvailabilityView.as_view(), 
         name='doctor-availability'),
]