from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allow anyone to read.
    Only staff users can create, update, or delete.
    """

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )