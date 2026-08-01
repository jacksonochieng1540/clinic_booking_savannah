from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.role == "admin" or request.user.is_superuser)


class IsDoctorUser(permissions.BasePermission):
    """
    Allows access only to doctor users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.role == "doctor")


class IsPatientUser(permissions.BasePermission):
    """
    Allows access only to patient users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.role == "patient")


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Allows access to doctor or admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role in ["doctor", "admin"] or request.user.is_superuser)
        )


class IsPatientOrAdmin(permissions.BasePermission):
    """
    Allows access to patient or admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role in ["patient", "admin"] or request.user.is_superuser)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin" or request.user.is_superuser:
            return True

        if hasattr(obj, "patient") and obj.patient.user == request.user:
            return True

        if hasattr(obj, "doctor") and obj.doctor.user == request.user:
            return True

        return False
