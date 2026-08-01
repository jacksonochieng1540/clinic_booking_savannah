from django.urls import path

from . import views

urlpatterns = [
    path("api/", views.DoctorListView.as_view(), name="doctor-list"),
    path("api/create/", views.DoctorCreateView.as_view(), name="doctor-create"),
    path("api/<int:id>/", views.DoctorDetailView.as_view(), name="doctor-detail"),
    path("api/<int:id>/update/", views.DoctorUpdateView.as_view(), name="doctor-update"),
]
