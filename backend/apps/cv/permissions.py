from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrReadOnly(BasePermission):
    """Allow read access to everyone; write access only to admin/staff users."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
