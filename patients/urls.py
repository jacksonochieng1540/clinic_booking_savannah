from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.PatientListView.as_view(), name='patient-list'),
    path('api/<int:id>/', views.PatientDetailView.as_view(), name='patient-detail'),
    path('api/<int:id>/update/', views.PatientUpdateView.as_view(), name='patient-update'),
]