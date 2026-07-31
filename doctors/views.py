from rest_framework import generics, permissions
from .models import Doctor
from .serializers import DoctorSerializer, DoctorListSerializer
from core.permissions import IsAdminUser, IsDoctorUser

class DoctorListView(generics.ListAPIView):
    """List all doctors"""
    permission_classes = [permissions.AllowAny]
    queryset = Doctor.objects.filter(is_available=True)
    serializer_class = DoctorListSerializer
    search_fields = ['user__first_name', 'user__last_name', 'specialty']
    ordering_fields = ['user__first_name', 'consultation_fee']

class DoctorDetailView(generics.RetrieveAPIView):
    """Get doctor details"""
    permission_classes = [permissions.AllowAny]
    queryset = Doctor.objects.filter(is_available=True)
    serializer_class = DoctorSerializer
    lookup_field = 'id'

class DoctorCreateView(generics.CreateAPIView):
    """Create a new doctor (Admin only)"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class DoctorUpdateView(generics.UpdateAPIView):
    """Update doctor details (Doctor or Admin)"""
    permission_classes = [permissions.IsAuthenticated, IsDoctorUser | IsAdminUser]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Doctor.objects.all()
        return Doctor.objects.filter(user=self.request.user)