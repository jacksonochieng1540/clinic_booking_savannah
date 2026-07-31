from rest_framework import generics, permissions
from .models import Patient
from .serializers import PatientSerializer
from core.permissions import IsPatientUser, IsAdminUser

class PatientListView(generics.ListAPIView):
    """List all patients (Admin only)"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    search_fields = ['user__first_name', 'user__last_name', 'user__email']

class PatientDetailView(generics.RetrieveAPIView):
    """Get patient details"""
    permission_classes = [permissions.IsAuthenticated, IsPatientUser | IsAdminUser]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Patient.objects.all()
        return Patient.objects.filter(user=self.request.user)

class PatientUpdateView(generics.UpdateAPIView):
    """Update patient details"""
    permission_classes = [permissions.IsAuthenticated, IsPatientUser | IsAdminUser]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Patient.objects.all()
        return Patient.objects.filter(user=self.request.user)