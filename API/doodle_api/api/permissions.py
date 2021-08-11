from rest_framework import permissions
from api.models import User


class IsStaff(permissions.BasePermission):
    """
        Custom permission to only allow staff to do actions.
    """
    def has_permission(self, request, view):
        is_staff = User.objects.get(id=request.user.id).is_staff

        return is_staff

