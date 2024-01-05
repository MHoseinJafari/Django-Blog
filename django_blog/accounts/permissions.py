from rest_framework import permissions


"""
generate verified permissions for the project

"""


class IsVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_verified


class IsVerifiedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_verified
        )